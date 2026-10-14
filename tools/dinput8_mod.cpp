#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <cstdint>
#include <dinput.h>
#include <stdio.h>
#include <stdarg.h>
#include <vector>
#include <string>
#include <algorithm>
#include "MinHook.h"

#pragma comment(lib, "user32.lib")

static FILE* g_logFile = nullptr;
static CRITICAL_SECTION g_cs;

void Log(const char* fmt, ...)
{
    EnterCriticalSection(&g_cs);
    if (g_logFile) {
        va_list args;
        va_start(args, fmt);
        vfprintf(g_logFile, fmt, args);
        va_end(args);
        fprintf(g_logFile, "\n");
        fflush(g_logFile);
    }
    LeaveCriticalSection(&g_cs);
}

struct EntryInfo {
    int id;
    uint64_t offset;
    uint64_t size;
    uint64_t zsize;
    uint64_t zip;
};

static EntryInfo g_entries[13000];
static int g_totalEntries = 0;

void LoadIdx()
{
    FILE* f = fopen("LINKDATA.IDX", "rb");
    if (!f) {
        Log("[-] Could not open LINKDATA.IDX");
        return;
    }
    uint8_t buf[32];
    int id = 0;
    while (fread(buf, 1, 32, f) == 32 && id < 13000) {
        uint64_t off = *(uint64_t*)(buf);
        uint64_t sz = *(uint64_t*)(buf + 8);
        uint64_t zsz = *(uint64_t*)(buf + 16);
        uint64_t zip = *(uint64_t*)(buf + 24);
        g_entries[id] = {id, off, sz, zsz, zip};
        id++;
    }
    g_totalEntries = id;
    fclose(f);
    Log("[+] Loaded %d entries from LINKDATA.IDX", g_totalEntries);
}

int FindEntryByOffset(uint64_t off)
{
    for (int i = 0; i < g_totalEntries; i++) {
        if (g_entries[i].size == 0) continue;
        uint64_t end = g_entries[i].offset + (g_entries[i].zip ? g_entries[i].zsize : g_entries[i].size);
        if (off >= g_entries[i].offset && off < end) {
            return i;
        }
    }
    return -1;
}

struct AddonEntry {
    uint32_t entry_id;
    uint64_t linkdata_offset;
    uint64_t linkdata_size;
    uint64_t data_len;
    uint8_t* data;
};

static std::vector<AddonEntry> g_addonEntries;
static HANDLE g_hLinkDataBin = INVALID_HANDLE_VALUE;

void LoadAddonPackage()
{
    FILE* f = fopen("dqh2_font_addons.bin", "rb");
    if (!f) {
        Log("[-] dqh2_font_addons.bin not found");
        return;
    }

    char magic[8];
    if (fread(magic, 1, 8, f) != 8 || memcmp(magic, "DQH2THAI", 8) != 0) {
        Log("[-] Invalid magic in dqh2_font_addons.bin");
        fclose(f);
        return;
    }

    uint32_t num_entries = 0;
    if (fread(&num_entries, 1, 4, f) != 4) {
        fclose(f);
        return;
    }

    Log("[+] Loading %u addon entries from dqh2_font_addons.bin...", num_entries);

    for (uint32_t i = 0; i < num_entries; i++) {
        AddonEntry e;
        if (fread(&e.entry_id, 1, 4, f) != 4) break;
        if (fread(&e.linkdata_offset, 1, 8, f) != 8) break;
        if (fread(&e.linkdata_size, 1, 8, f) != 8) break;
        if (fread(&e.data_len, 1, 8, f) != 8) break;
        e.data = (uint8_t*)malloc(e.data_len);
        if (e.data) {
            fread(e.data, 1, e.data_len, f);
            g_addonEntries.push_back(e);
            Log("    [Entry #%4u] Offset: %11llu, Modded Size: %8llu bytes",
                e.entry_id, e.linkdata_offset, e.data_len);
        }
    }
    fclose(f);
    Log("[+] Addon package successfully loaded into memory!");
}

// Real DirectInput8Create proxy
typedef HRESULT (WINAPI *tDirectInput8Create)(HINSTANCE hinst, DWORD dwVersion, REFIID riidltf, LPVOID *ppvOut, LPUNKNOWN punkOuter);
static tDirectInput8Create oDirectInput8Create = nullptr;

extern "C" __declspec(dllexport) HRESULT WINAPI DirectInput8Create(
    HINSTANCE hinst, DWORD dwVersion, REFIID riidltf, LPVOID *ppvOut, LPUNKNOWN punkOuter)
{
    if (!oDirectInput8Create) {
        char sysPath[MAX_PATH];
        GetSystemDirectoryA(sysPath, MAX_PATH);
        strcat_s(sysPath, "\\dinput8.dll");
        HMODULE hOrig = LoadLibraryA(sysPath);
        if (hOrig) {
            oDirectInput8Create = (tDirectInput8Create)GetProcAddress(hOrig, "DirectInput8Create");
        }
    }
    if (oDirectInput8Create) {
        return oDirectInput8Create(hinst, dwVersion, riidltf, ppvOut, punkOuter);
    }
    return E_FAIL;
}

// Hook CreateFileW
typedef HANDLE (WINAPI *tCreateFileW)(LPCWSTR lpFileName, DWORD dwDesiredAccess, DWORD dwShareMode,
                                     LPSECURITY_ATTRIBUTES lpSecurityAttributes, DWORD dwCreationDisposition,
                                     DWORD dwFlagsAndAttributes, HANDLE hTemplateFile);
static tCreateFileW oCreateFileW = nullptr;

HANDLE WINAPI hkCreateFileW(LPCWSTR lpFileName, DWORD dwDesiredAccess, DWORD dwShareMode,
                            LPSECURITY_ATTRIBUTES lpSecurityAttributes, DWORD dwCreationDisposition,
                            DWORD dwFlagsAndAttributes, HANDLE hTemplateFile)
{
    HANDLE h = oCreateFileW(lpFileName, dwDesiredAccess, dwShareMode, lpSecurityAttributes,
                            dwCreationDisposition, dwFlagsAndAttributes, hTemplateFile);
    if (lpFileName && h != INVALID_HANDLE_VALUE) {
        std::wstring ws(lpFileName);
        if (ws.find(L"LINKDATA.BIN") != std::wstring::npos || ws.find(L"linkdata.bin") != std::wstring::npos) {
            g_hLinkDataBin = h;
            Log("[FILE OPEN] LINKDATA.BIN handle = %p", h);
        }
    }
    return h;
}

// Hook ReadFile
typedef BOOL (WINAPI *tReadFile)(HANDLE hFile, LPVOID lpBuffer, DWORD nNumberOfBytesToRead,
                                 LPDWORD lpNumberOfBytesRead, LPOVERLAPPED lpOverlapped);
static tReadFile oReadFile = nullptr;

BOOL WINAPI hkReadFile(HANDLE hFile, LPVOID lpBuffer, DWORD nNumberOfBytesToRead,
                       LPDWORD lpNumberOfBytesRead, LPOVERLAPPED lpOverlapped)
{
    uint64_t off = 0;
    bool isLinkData = (hFile == g_hLinkDataBin);
    if (isLinkData) {
        if (lpOverlapped) {
            off = ((uint64_t)lpOverlapped->OffsetHigh << 32) | lpOverlapped->Offset;
        } else {
            LONG high = 0;
            DWORD low = SetFilePointer(hFile, 0, &high, FILE_CURRENT);
            off = ((uint64_t)high << 32) | low;
        }
        int eid = FindEntryByOffset(off);
        if (eid != -1) {
            Log("[READ] Entry #%4d (off: %11lld, size: %8lld, read: %6u, zip: %d)",
                eid, off, g_entries[eid].size, nNumberOfBytesToRead, (int)g_entries[eid].zip);
        }
    }

    BOOL ret = oReadFile(hFile, lpBuffer, nNumberOfBytesToRead, lpNumberOfBytesRead, lpOverlapped);

    if (ret && isLinkData && lpNumberOfBytesRead && *lpNumberOfBytesRead > 0) {
        uint64_t read_start = off;
        uint64_t read_end = off + *lpNumberOfBytesRead;

        for (const auto& entry : g_addonEntries) {
            uint64_t entry_start = entry.linkdata_offset;
            uint64_t entry_end = entry.linkdata_offset + entry.data_len;

            if (read_end > entry_start && read_start < entry_end) {
                uint64_t overlap_start = (std::max)(read_start, entry_start);
                uint64_t overlap_end = (std::min)(read_end, entry_end);
                if (overlap_end > overlap_start) {
                    uint64_t copy_len = overlap_end - overlap_start;
                    uint64_t buf_offset = overlap_start - read_start;
                    uint64_t src_offset = overlap_start - entry_start;
                    memcpy((uint8_t*)lpBuffer + buf_offset, entry.data + src_offset, (size_t)copy_len);
                    Log("    >>> [VIRTUAL OVERRIDE] Entry #%u patched in RAM (%llu bytes at rel_off %llu)",
                        entry.entry_id, copy_len, src_offset);
                }
            }
        }
    }

    return ret;
}

DWORD WINAPI InitThread(LPVOID)
{
    InitializeCriticalSection(&g_cs);
    g_logFile = fopen("file_access.log", "w");
    Log("=== Dragon Quest Heroes II Mod & File Access Logger Started ===");

    LoadIdx();
    LoadAddonPackage();

    if (MH_Initialize() == MH_OK) {
        MH_CreateHookApi(L"kernel32.dll", "CreateFileW", (LPVOID)&hkCreateFileW, (LPVOID*)&oCreateFileW);
        MH_CreateHookApi(L"kernel32.dll", "ReadFile", (LPVOID)&hkReadFile, (LPVOID*)&oReadFile);
        MH_EnableHook(MH_ALL_HOOKS);
        Log("[+] Hooks successfully initialized!");
    }
    return 0;
}

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved)
{
    if (fdwReason == DLL_PROCESS_ATTACH) {
        DisableThreadLibraryCalls(hinstDLL);
        CreateThread(nullptr, 0, InitThread, nullptr, 0, nullptr);
    } else if (fdwReason == DLL_PROCESS_DETACH) {
        MH_DisableHook(MH_ALL_HOOKS);
        MH_Uninitialize();
        if (g_logFile) {
            Log("=== Game Closed. Logger finished. ===");
            fclose(g_logFile);
        }
        DeleteCriticalSection(&g_cs);
    }
    return TRUE;
}

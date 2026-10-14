#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <cstdint>
#include <dinput.h>
#include <stdio.h>
#include <stdarg.h>
#include <vector>
#include <string>
#include "MinHook.h"

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
static HANDLE g_hLinkDataBin = INVALID_HANDLE_VALUE;

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

// Real DirectInput8Create
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

static int g_readCount = 0;

BOOL WINAPI hkReadFile(HANDLE hFile, LPVOID lpBuffer, DWORD nNumberOfBytesToRead,
                       LPDWORD lpNumberOfBytesRead, LPOVERLAPPED lpOverlapped)
{
    if (hFile == g_hLinkDataBin) {
        uint64_t off = 0;
        if (lpOverlapped) {
            off = ((uint64_t)lpOverlapped->OffsetHigh << 32) | lpOverlapped->Offset;
        } else {
            LONG high = 0;
            DWORD low = SetFilePointer(hFile, 0, &high, FILE_CURRENT);
            off = ((uint64_t)high << 32) | low;
        }
        int eid = FindEntryByOffset(off);
        if (eid != -1) {
            Log("[READ LINKDATA] Entry #%4d (off: %11lld, size: %8lld, read: %6u, zip: %d)",
                eid, off, g_entries[eid].size, nNumberOfBytesToRead, (int)g_entries[eid].zip);
        } else {
            Log("[READ LINKDATA] Unknown off: %lld, read: %u", off, nNumberOfBytesToRead);
        }
    }
    return oReadFile(hFile, lpBuffer, nNumberOfBytesToRead, lpNumberOfBytesRead, lpOverlapped);
}

// Hook CreateFontIndirectA
typedef HFONT (WINAPI *tCreateFontIndirectA)(const LOGFONTA *lplf);
static tCreateFontIndirectA oCreateFontIndirectA = nullptr;

HFONT WINAPI hkCreateFontIndirectA(const LOGFONTA *lplf)
{
    if (lplf) {
        Log("[GDI FONT] Face='%s', Height=%d, Weight=%d, CharSet=%d",
            lplf->lfFaceName, lplf->lfHeight, lplf->lfWeight, lplf->lfCharSet);
    }
    return oCreateFontIndirectA(lplf);
}

void StartHook()
{
    InitializeCriticalSection(&g_cs);
    g_logFile = fopen("file_access.log", "w");
    Log("=== Dragon Quest Heroes II File Access Logger Started ===");
    LoadIdx();

    MH_Initialize();
    MH_CreateHookApi(L"kernel32.dll", "CreateFileW", (LPVOID)hkCreateFileW, (LPVOID*)&oCreateFileW);
    MH_CreateHookApi(L"kernel32.dll", "ReadFile", (LPVOID)hkReadFile, (LPVOID*)&oReadFile);
    MH_CreateHookApi(L"gdi32.dll", "CreateFontIndirectA", (LPVOID)hkCreateFontIndirectA, (LPVOID*)&oCreateFontIndirectA);
    MH_EnableHook(MH_ALL_HOOKS);
    Log("[+] All hooks installed successfully!");
}

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved)
{
    if (fdwReason == DLL_PROCESS_ATTACH) {
        DisableThreadLibraryCalls(hinstDLL);
        CreateThread(nullptr, 0, (LPTHREAD_START_ROUTINE)StartHook, nullptr, 0, nullptr);
    } else if (fdwReason == DLL_PROCESS_DETACH) {
        MH_DisableHook(MH_ALL_HOOKS);
        MH_Uninitialize();
        if (g_logFile) {
            fclose(g_logFile);
        }
        DeleteCriticalSection(&g_cs);
    }
    return TRUE;
}

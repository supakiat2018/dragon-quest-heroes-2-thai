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

// =========================================================================
// Font Advance Width Hook (Proportional Spacing)
// =========================================================================

struct CharInfo {
    uint32_t char_code;    // +0x00: UTF-8 character code
    uint32_t byte_len;     // +0x04: 1, 2, 3, or 4 bytes
    uint32_t glyph_index;  // +0x08: cell index in font atlas
    float advance_width;   // +0x0C: spacing / cursor advance
    uint8_t flags[4];      // +0x10
};

typedef const char* (*tGetNextCharAndWidth)(void* mgr, const char* str, CharInfo* out_info);
static tGetNextCharAndWidth oGetNextCharAndWidth = nullptr;

float GetThaiCharWidth(uint32_t code)
{
    switch (code) {
        // Standard menu tokens:
        case 0xD0B3: return 16.0f; // เ (г)
        case 0xD0B5: return 18.0f; // า (е)
        case 0xD18C: return 19.0f; // ร (ь)
        case 0xD181: return 18.0f; // ร้ (с)
        case 0xD182: return 19.0f; // ร์ (т)
        case 0xD0B2: return 18.0f; // จ (в)
        case 0xD0B0: return 20.0f; // ก (а)
        case 0xD0BE: return 20.0f; // ม (о)
        case 0xD0B8: return 20.0f; // น (и)
        case 0xD180: return 21.0f; // ส (р)
        case 0xD0B1: return 19.0f; // ง (б)
        case 0xD0BA: return 21.0f; // ด (к)
        case 0xD0BD: return 21.0f; // ท (н)
        case 0xD0BB: return 22.0f; // ล (л)
        case 0xD0B4: return 22.0f; // บ (д)
        case 0xD183: return 22.0f; // อ (у)
        case 0xD091: return 23.0f; // ดิ (Б)
        case 0xD093: return 21.0f; // ค่ (Г)
        case 0xD092: return 23.0f; // คี (В)
        case 0xD095: return 23.0f; // ฟิ (Е)
        case 0xD18D: return 17.0f; // ริ่ (э)
        case 0xD187: return 20.0f; // ทึ (ч)
        case 0xD18A: return 22.0f; // ตั้ (ъ)
        case 0xD0A0: return 23.0f; // บั (Р)
        case 0xD090: return 28.0f; // ย์ (А)
        case 0xD188: return 27.0f; // ส์ (ш)
        case 0xD185: return 20.0f; // ต้ (х)
        case 0xD191: return 18.0f; // ช่ (ё)
        case 0xD0B7: return 16.0f; // ใ (з)

        // Tight syllable pairs:
        case 0xD094: return 32.0f; // ต้อ (Д)
        case 0xD096: return 30.0f; // กา  (Ж)
        case 0xD097: return 32.0f; // สร้ (З)
        case 0xD098: return 30.0f; // เดิ (И)
        case 0xD099: return 30.0f; // ทา  (Й)
        case 0xD09A: return 30.0f; // ใน  (К)
        case 0xD09B: return 32.0f; // ช่อ (Л)
        case 0xD09C: return 30.0f; // ใด  (М)

        default:
            return -1.0f;
    }
}

const char* hkGetNextCharAndWidth(void* mgr, const char* str, CharInfo* out_info)
{
    const char* ret = oGetNextCharAndWidth(mgr, str, out_info);
    if (out_info && out_info->byte_len == 2) {
        float custom_w = GetThaiCharWidth(out_info->char_code);
        if (custom_w > 0.0f) {
            float orig_w = out_info->advance_width;
            out_info->advance_width = custom_w;
            static bool logged[65536] = { false };
            uint16_t key = (uint16_t)out_info->char_code;
            if (!logged[key]) {
                logged[key] = true;
                Log("[FONT WIDTH HOOK] char_code: 0x%04X, glyph: %u, width: %.1f -> %.1f",
                    out_info->char_code, out_info->glyph_index, orig_w, custom_w);
            }
        }
    }
    return ret;
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

        uintptr_t exeBase = (uintptr_t)GetModuleHandle(NULL);
        uintptr_t targetFontFn = exeBase + 0x56a500;
        const uint8_t expected_prologue[] = { 0x48, 0x89, 0x5c, 0x24, 0x08, 0x48, 0x89, 0x74 };
        if (memcmp((const void*)targetFontFn, expected_prologue, sizeof(expected_prologue)) == 0) {
            Log("[+] Verified GetNextCharAndWidth prologue at %p, creating hook...", (void*)targetFontFn);
            if (MH_CreateHook((LPVOID)targetFontFn, (LPVOID)&hkGetNextCharAndWidth, (LPVOID*)&oGetNextCharAndWidth) == MH_OK) {
                Log("[+] Successfully hooked GetNextCharAndWidth for Proportional Font Spacing!");
            } else {
                Log("[-] Failed to create hook on GetNextCharAndWidth");
            }
        } else {
            Log("[-] Prologue mismatch at %p, skipping font advance width hook", (void*)targetFontFn);
        }

        MH_EnableHook(MH_ALL_HOOKS);
        Log("[+] Hooks successfully initialized and enabled!");
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

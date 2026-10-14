#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <cstdint>
#include <dinput.h>
#include <stdio.h>
#include <vector>
#include <string>
#include <algorithm>
#include "MinHook.h"

#pragma comment(lib, "user32.lib")

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
    if (!f) return;

    char magic[8];
    if (fread(magic, 1, 8, f) != 8 || memcmp(magic, "DQH2THAI", 8) != 0) {
        fclose(f);
        return;
    }

    uint32_t num_entries = 0;
    if (fread(&num_entries, 1, 4, f) != 4) {
        fclose(f);
        return;
    }

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
        }
    }
    fclose(f);
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
                }
            }
        }
    }

    return ret;
}

DWORD WINAPI InitThread(LPVOID)
{
    LoadAddonPackage();

    if (MH_Initialize() == MH_OK) {
        MH_CreateHookApi(L"kernel32.dll", "CreateFileW", (LPVOID)&hkCreateFileW, (LPVOID*)&oCreateFileW);
        MH_CreateHookApi(L"kernel32.dll", "ReadFile", (LPVOID)&hkReadFile, (LPVOID*)&oReadFile);
        MH_EnableHook(MH_ALL_HOOKS);
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
    }
    return TRUE;
}

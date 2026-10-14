#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <d3d11.h>
#include <dxgi.h>
#include <d2d1.h>
#include <dwrite.h>
#include <dinput.h>
#include <stdio.h>
#include <stdarg.h>
#include <string>
#include "MinHook.h"

void Log(const char* fmt, ...)
{
    FILE* f = fopen("dinput8.log", "a");
    if (!f) return;
    va_list args;
    va_start(args, fmt);
    vfprintf(f, fmt, args);
    va_end(args);
    fprintf(f, "\n");
    fclose(f);
}

typedef HRESULT (WINAPI *tDirectInput8Create)(HINSTANCE hinst, DWORD dwVersion, REFIID riidltf, LPVOID *ppvOut, LPUNKNOWN punkOuter);
tDirectInput8Create oDirectInput8Create = nullptr;

typedef HRESULT (WINAPI *tPresent)(IDXGISwapChain* pSwapChain, UINT SyncInterval, UINT Flags);
tPresent oPresent = nullptr;

ID2D1Factory* pD2DFactory = nullptr;
IDWriteFactory* pDWriteFactory = nullptr;
ID2D1RenderTarget* pD2DRenderTarget = nullptr;
IDWriteTextFormat* pTextFormatLarge = nullptr;
IDWriteTextFormat* pTextFormatSmall = nullptr;
ID2D1SolidColorBrush* pWhiteBrush = nullptr;
ID2D1SolidColorBrush* pShadowBrush = nullptr;
ID2D1SolidColorBrush* pGoldBrush = nullptr;

bool g_d2dInitialized = false;

extern "C" __declspec(dllexport) HRESULT WINAPI DirectInput8Create(
    HINSTANCE hinst, DWORD dwVersion, REFIID riidltf, LPVOID *ppvOut, LPUNKNOWN punkOuter)
{
    Log("DirectInput8Create called (dwVersion=0x%X)", dwVersion);
    if (!oDirectInput8Create) {
        char sysPath[MAX_PATH];
        GetSystemDirectoryA(sysPath, MAX_PATH);
        strcat_s(sysPath, "\\dinput8.dll");
        HMODULE hOrig = LoadLibraryA(sysPath);
        if (hOrig) {
            oDirectInput8Create = (tDirectInput8Create)GetProcAddress(hOrig, "DirectInput8Create");
            Log("Loaded real dinput8 from %s (proc=%p)", sysPath, oDirectInput8Create);
        } else {
            Log("Failed to load real dinput8.dll!");
        }
    }
    if (oDirectInput8Create) {
        return oDirectInput8Create(hinst, dwVersion, riidltf, ppvOut, punkOuter);
    }
    return E_FAIL;
}

void DrawThaiText(const std::wstring& text, float x, float y, float w, float h, IDWriteTextFormat* format, ID2D1SolidColorBrush* brush, bool shadow = true)
{
    if (!pD2DRenderTarget) return;
    D2D1_RECT_F rect = D2D1::RectF(x, y, x + w, y + h);
    if (shadow) {
        D2D1_RECT_F shadowRect = D2D1::RectF(x + 2.0f, y + 2.0f, x + w + 2.0f, y + h + 2.0f);
        pD2DRenderTarget->DrawText(text.c_str(), (UINT32)text.length(), format, &shadowRect, pShadowBrush);
    }
    pD2DRenderTarget->DrawText(text.c_str(), (UINT32)text.length(), format, &rect, brush);
}

bool InitD2D(IDXGISwapChain* pSwapChain)
{
    if (g_d2dInitialized) return true;

    IDXGISurface* pBackBufferSurface = nullptr;
    HRESULT hr = pSwapChain->GetBuffer(0, __uuidof(IDXGISurface), (void**)&pBackBufferSurface);
    if (FAILED(hr) || !pBackBufferSurface) {
        static bool loggedOnce = false;
        if (!loggedOnce) {
            Log("InitD2D: GetBuffer(IDXGISurface) failed with hr=0x%08X", hr);
            loggedOnce = true;
        }
        return false;
    }

    if (!pD2DFactory) {
        D2D1CreateFactory(D2D1_FACTORY_TYPE_SINGLE_THREADED, &pD2DFactory);
    }

    if (!pDWriteFactory) {
        DWriteCreateFactory(DWRITE_FACTORY_TYPE_SHARED, __uuidof(IDWriteFactory), (IUnknown**)&pDWriteFactory);
    }

    D2D1_RENDER_TARGET_PROPERTIES props = D2D1::RenderTargetProperties(
        D2D1_RENDER_TARGET_TYPE_DEFAULT,
        D2D1::PixelFormat(DXGI_FORMAT_UNKNOWN, D2D1_ALPHA_MODE_PREMULTIPLIED)
    );

    hr = pD2DFactory->CreateDxgiSurfaceRenderTarget(pBackBufferSurface, &props, &pD2DRenderTarget);
    pBackBufferSurface->Release();
    if (FAILED(hr) || !pD2DRenderTarget) {
        static bool loggedOnce2 = false;
        if (!loggedOnce2) {
            Log("InitD2D: CreateDxgiSurfaceRenderTarget failed with hr=0x%08X", hr);
            loggedOnce2 = true;
        }
        return false;
    }

    pD2DRenderTarget->CreateSolidColorBrush(D2D1::ColorF(D2D1::ColorF::White), &pWhiteBrush);
    pD2DRenderTarget->CreateSolidColorBrush(D2D1::ColorF(0.0f, 0.0f, 0.0f, 0.85f), &pShadowBrush);
    pD2DRenderTarget->CreateSolidColorBrush(D2D1::ColorF(1.0f, 0.84f, 0.0f, 1.0f), &pGoldBrush);

    pDWriteFactory->CreateTextFormat(
        L"Leelawadee UI",
        NULL,
        DWRITE_FONT_WEIGHT_BOLD,
        DWRITE_FONT_STYLE_NORMAL,
        DWRITE_FONT_STRETCH_NORMAL,
        24.0f,
        L"th-TH",
        &pTextFormatLarge
    );

    pDWriteFactory->CreateTextFormat(
        L"Leelawadee UI",
        NULL,
        DWRITE_FONT_WEIGHT_NORMAL,
        DWRITE_FONT_STYLE_NORMAL,
        DWRITE_FONT_STRETCH_NORMAL,
        18.0f,
        L"th-TH",
        &pTextFormatSmall
    );

    Log("InitD2D: Direct2D & DirectWrite initialized successfully!");
    g_d2dInitialized = true;
    return true;
}

HRESULT WINAPI Hooked_Present(IDXGISwapChain* pSwapChain, UINT SyncInterval, UINT Flags)
{
    static int frameCount = 0;
    frameCount++;
    if (frameCount == 1 || frameCount == 60) {
        Log("Hooked_Present: called (frame %d, pSwapChain=%p)", frameCount, pSwapChain);
    }

    if (InitD2D(pSwapChain)) {
        pD2DRenderTarget->BeginDraw();
        DrawThaiText(L"✦ DRAGON QUEST HEROES II - ม็อดภาษาไทย (DirectX 11 Hook ทำงานสมบูรณ์) ✦", 20.0f, 15.0f, 800.0f, 30.0f, pTextFormatSmall, pGoldBrush);
        pD2DRenderTarget->EndDraw();
    }

    return oPresent(pSwapChain, SyncInterval, Flags);
}

DWORD WINAPI HookThread(LPVOID lpParam)
{
    Log("HookThread: Started, sleeping 1500ms...");
    Sleep(1500);

    WNDCLASSA wc = {};
    wc.lpfnWndProc = DefWindowProcA;
    wc.hInstance = GetModuleHandleA(NULL);
    wc.lpszClassName = "DummyDXGIClass";
    RegisterClassA(&wc);

    HWND hWndDummy = CreateWindowA(wc.lpszClassName, "Dummy", WS_OVERLAPPEDWINDOW, 0, 0, 100, 100, NULL, NULL, wc.hInstance, NULL);
    if (!hWndDummy) {
        Log("HookThread: Failed to create dummy window!");
        return 0;
    }

    DXGI_SWAP_CHAIN_DESC scDesc = {};
    scDesc.BufferCount = 1;
    scDesc.BufferDesc.Format = DXGI_FORMAT_R8G8B8A8_UNORM;
    scDesc.BufferUsage = DXGI_USAGE_RENDER_TARGET_OUTPUT;
    scDesc.OutputWindow = hWndDummy;
    scDesc.SampleDesc.Count = 1;
    scDesc.Windowed = TRUE;

    IDXGISwapChain* pDummySwapChain = nullptr;
    ID3D11Device* pDummyDevice = nullptr;
    D3D_FEATURE_LEVEL featureLevel;

    HRESULT hr = D3D11CreateDeviceAndSwapChain(
        NULL, D3D_DRIVER_TYPE_HARDWARE, NULL, 0, NULL, 0,
        D3D11_SDK_VERSION, &scDesc, &pDummySwapChain, &pDummyDevice, &featureLevel, NULL);

    Log("HookThread: D3D11CreateDeviceAndSwapChain returned hr=0x%08X", hr);

    if (SUCCEEDED(hr) && pDummySwapChain) {
        void** vtable = *(void***)pDummySwapChain;
        void* pPresentTarget = vtable[8]; // IDXGISwapChain::Present
        Log("HookThread: Found Present address at %p", pPresentTarget);

        pDummySwapChain->Release();
        pDummyDevice->Release();
        DestroyWindow(hWndDummy);
        UnregisterClassA(wc.lpszClassName, wc.hInstance);

        MH_STATUS mInit = MH_Initialize();
        Log("HookThread: MH_Initialize = %d", mInit);
        if (mInit == MH_OK || mInit == MH_ERROR_ALREADY_INITIALIZED) {
            MH_STATUS mHook = MH_CreateHook(pPresentTarget, (LPVOID)&Hooked_Present, (LPVOID*)&oPresent);
            Log("HookThread: MH_CreateHook = %d", mHook);
            MH_STATUS mEnable = MH_EnableHook(pPresentTarget);
            Log("HookThread: MH_EnableHook = %d", mEnable);
        }
    } else {
        Log("HookThread: Could not create dummy SwapChain!");
        DestroyWindow(hWndDummy);
        UnregisterClassA(wc.lpszClassName, wc.hInstance);
    }

    return 0;
}

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved)
{
    if (fdwReason == DLL_PROCESS_ATTACH) {
        Log("=== DllMain: DLL_PROCESS_ATTACH in process PID %d ===", GetCurrentProcessId());
        DisableThreadLibraryCalls(hinstDLL);
        CreateThread(NULL, 0, HookThread, NULL, 0, NULL);
    } else if (fdwReason == DLL_PROCESS_DETACH) {
        Log("=== DllMain: DLL_PROCESS_DETACH ===");
        if (g_d2dInitialized) {
            if (pWhiteBrush) pWhiteBrush->Release();
            if (pShadowBrush) pShadowBrush->Release();
            if (pGoldBrush) pGoldBrush->Release();
            if (pTextFormatLarge) pTextFormatLarge->Release();
            if (pTextFormatSmall) pTextFormatSmall->Release();
            if (pD2DRenderTarget) pD2DRenderTarget->Release();
            if (pDWriteFactory) pDWriteFactory->Release();
            if (pD2DFactory) pD2DFactory->Release();
        }
        MH_Uninitialize();
    }
    return TRUE;
}

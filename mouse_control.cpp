#include <windows.h>
#include <iostream>

HHOOK mouseHook;
HHOOK keyboardHook;

typedef void (*MouseCallback)(int, int); // Define a function pointer type for the callback

MouseCallback callback = nullptr; // This will hold the Python callback

// Callback function to block mouse input
LRESULT CALLBACK MouseProc(int nCode, WPARAM wParam, LPARAM lParam) {
    if (nCode >= 0) {
        // Check for mouse movement event
        if (wParam == WM_MOUSEMOVE) {
            MOUSEHOOKSTRUCT* pMouseHook = (MOUSEHOOKSTRUCT*)lParam;
            int mouseX = pMouseHook->pt.x;
            int mouseY = pMouseHook->pt.y;
            
            std::cout << "MouseProc: Mouse moved to: (" << mouseX << ", " << mouseY << ")\n";

            if (callback) {
                std::cout << "MouseProc: Callback about to be called.\n";
                callback(mouseX, mouseY);
                std::cout << "MouseProc: Callback was called.\n";
            }
        }
    }
    return 1;
}


LRESULT CALLBACK KeyboardProc(int nCode, WPARAM wParam, LPARAM lParam) {
    return 1; // Returning non-zero blocks the event (prevents mouse movement)
}


extern "C" __declspec(dllexport) void SetMouseCallback(MouseCallback cb) {
    callback = cb;
    
}


extern "C" __declspec(dllexport) void EnableMouse(bool enable) {
    if (enable) {
        UnhookWindowsHookEx(mouseHook); // Remove hook to re-enable mouse
        mouseHook = NULL;
        UnhookWindowsHookEx(keyboardHook);
        keyboardHook = NULL;
        std::cout << "Mouse enabled.\n";
    } else {
        mouseHook = SetWindowsHookEx(WH_MOUSE_LL, MouseProc, NULL, 0);
        keyboardHook = SetWindowsHookEx(WH_KEYBOARD_LL, KeyboardProc, NULL, 0);
        std::cout << "Mouse disabled.\n";
    }
}

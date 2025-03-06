#include <windows.h>
#include <iostream>


HHOOK mouseHook;
HHOOK keyboardHook;

POINT cursorPos;

typedef void (*MouseCallback)(int, int); // Define a function pointer type for the callback

MouseCallback callback = nullptr; // This will hold the Python callback

bool is_lock = false;

LRESULT CALLBACK MouseProc(int nCode, WPARAM wParam, LPARAM lParam) {
    if (nCode >= 0) {
        // Check for mouse movement event
        if (wParam == WM_MOUSEMOVE) {
            MOUSEHOOKSTRUCT* pMouseHook = (MOUSEHOOKSTRUCT*)lParam;
            int mouseX = pMouseHook->pt.x;
            int mouseY = pMouseHook->pt.y;
            
            if (callback) {
                callback(mouseX, mouseY);
            }
        }
    }
    return is_lock ? 1 : 0;
}


LRESULT CALLBACK KeyboardProc(int nCode, WPARAM wParam, LPARAM lParam) {
    return 1; // Blocks mouse events
}


extern "C" __declspec(dllexport) void SetMouseCallback(MouseCallback cb) {
    callback = cb;
    mouseHook = SetWindowsHookEx(WH_MOUSE_LL, MouseProc, NULL, 0);
}


extern "C" __declspec(dllexport) void EnableMouse(bool enable) {
    is_lock = enable;
    if (enable) {
        // UnhookWindowsHookEx(mouseHook); // Remove hook to enable mouse
        UnhookWindowsHookEx(keyboardHook);
        keyboardHook = NULL;
        // mouseHook = NULL;
        std::cout << "Mouse enabled.\n";
    } else if(keyboardHook == NULL){
        keyboardHook = SetWindowsHookEx(WH_KEYBOARD_LL, KeyboardProc, NULL, 0);
        std::cout << "Mouse disabled.\n";
    }
}

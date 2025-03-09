#include <windows.h>
#include <iostream>

HHOOK mouseHook;
HHOOK keyboardHook;

typedef void (*MouseCallback)(int, int); // Define a function pointer type for the callback

MouseCallback callback = nullptr; // This will hold the Python callback

bool is_locked = false;

// Callback function to block mouse input
LRESULT CALLBACK MouseProc(int nCode, WPARAM wParam, LPARAM lParam) {
    if (nCode >= 0) {
        if (wParam == WM_MOUSEMOVE) {
            MOUSEHOOKSTRUCT* pMouseHook = (MOUSEHOOKSTRUCT*)lParam;
            int mouseX = pMouseHook->pt.x;
            int mouseY = pMouseHook->pt.y;

            if (callback) {
                callback(mouseX, mouseY);
            }   
        }
    }
    if (is_locked) { // check if mouse should be locked
        return 1; // Consume the event, preventing movement.
    }
    return CallNextHookEx(mouseHook, nCode, wParam, lParam);
}


LRESULT CALLBACK KeyboardProc(int nCode, WPARAM wParam, LPARAM lParam) {
    if (is_locked && nCode >= 0) {
        return 1;
    }
    return CallNextHookEx(keyboardHook, nCode, wParam, lParam);
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
        is_locked = false;
        std::cout << "Mouse enabled.\n";
    } else if (keyboardHook == NULL && mouseHook == NULL){
        is_locked = true;
        mouseHook = SetWindowsHookEx(WH_MOUSE_LL, MouseProc, NULL, 0);
        keyboardHook = SetWindowsHookEx(WH_KEYBOARD_LL, KeyboardProc, NULL, 0);
        std::cout << "Mouse disabled.\n";
    }
}

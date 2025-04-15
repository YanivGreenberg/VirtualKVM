#include <windows.h>
#include <iostream>

HHOOK mouseHook;
HHOOK keyboardHook;

typedef void (*MouseCallback)(int, int); // Define a function pointer type for the callback

typedef void (*MouseClickCallback)(int);

typedef void (*KeyboardCallback)(int, bool, bool);

typedef void (*MouseScrollCallback)(int);  


MouseCallback callback = nullptr; // This will hold the Python callback
MouseClickCallback clickCallback = nullptr;
KeyboardCallback keyboardCallback = nullptr; 
MouseScrollCallback scrollCallback = nullptr;


bool is_locked = false;

#define LEFT_CLICK 1
#define RIGHT_CLICK 2
#define MIDDLE_CLICK 3


LRESULT CALLBACK MouseProc(int nCode, WPARAM wParam, LPARAM lParam) {
    if (nCode >= 0) {
        MOUSEHOOKSTRUCT* pMouseHook = (MOUSEHOOKSTRUCT*)lParam;
        int mouseX = pMouseHook->pt.x;
        int mouseY = pMouseHook->pt.y;

        if (wParam == WM_MOUSEMOVE && callback) {
            callback(mouseX, mouseY);
        } 
        else if (wParam == WM_LBUTTONDOWN || wParam == WM_RBUTTONDOWN || wParam == WM_MBUTTONDOWN) {
            if (clickCallback) {
                int buttonType = 0;
                if (wParam == WM_LBUTTONDOWN) buttonType = 1;  // Left Click
                if (wParam == WM_RBUTTONDOWN) buttonType = 2;  // Right Click
                if (wParam == WM_MBUTTONDOWN) buttonType = 3;  // Middle Click
                
                std::cout << "Mouse Click Event: " << buttonType << std::endl;  // Debug print
                clickCallback(buttonType);
            }
        }
        else if (wParam == WM_MOUSEWHEEL && scrollCallback) {
            MSLLHOOKSTRUCT* pMouseHookLL = (MSLLHOOKSTRUCT*)lParam;
            short delta = (short)HIWORD(pMouseHookLL->mouseData);
        
            std::cout << "Mouse Scroll Event: " << delta << std::endl;
            scrollCallback(delta);
        }
        
        
    }
    if (is_locked) { // check if mouse should be locked
        return 1; // Consume the event, preventing movement.
    }
    return CallNextHookEx(mouseHook, nCode, wParam, lParam);
}


LRESULT CALLBACK KeyboardProc(int nCode, WPARAM wParam, LPARAM lParam) {
    if (nCode >= 0 && keyboardCallback) {
        KBDLLHOOKSTRUCT* pKeyboard = (KBDLLHOOKSTRUCT*)lParam;
        int keyCode = pKeyboard->vkCode;
        bool isPressed = (wParam == WM_KEYDOWN || wParam == WM_SYSKEYDOWN);

        // Check if Shift is held down
        bool shiftPressed = (GetKeyState(VK_SHIFT) & 0x8000) != 0;

        // Check if Caps Lock is on
        bool capsLockOn = (GetKeyState(VK_CAPITAL) & 0x0001) != 0;

        // Determine if the key is uppercase
        bool isUppercase = (capsLockOn ^ shiftPressed);  // XOR: Caps Lock and Shift cancel each other


        // Call Python Callback
        keyboardCallback(keyCode, isPressed, isUppercase);
    }

    if (is_locked) {
        return 1; // Block keyboard input
    }
    return CallNextHookEx(keyboardHook, nCode, wParam, lParam);
}


extern "C" __declspec(dllexport) void SetMouseCallback(MouseCallback cb) {
    callback = cb;  
}

extern "C" __declspec(dllexport) void SetMouseClickCallback(MouseClickCallback cb) {
    clickCallback = cb;
}

extern "C" __declspec(dllexport) void SetKeyboardCallback(KeyboardCallback cb) {
    keyboardCallback = cb;
}
extern "C" __declspec(dllexport) void SetMouseScrollCallback(MouseScrollCallback cb) {
    scrollCallback = cb;
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

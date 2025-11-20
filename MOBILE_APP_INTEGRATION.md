# 모바일 앱 연동 가이드

이 문서는 Mozik 웹 애플리케이션을 모바일 앱과 연동하는 방법을 설명합니다.

## 📱 개요

모바일 앱에서 웹뷰(WebView)를 사용하여 로그인, 회원가입 등 인증 관련 기능을 웹으로 처리하고, 앱 내에서 결과를 확인할 수 있도록 구성합니다.

## 🔧 Flask 앱 설정

### 1. 세션 쿠키 설정

`app.py`에서 이미 다음 설정이 적용되어 있습니다:

```python
app.config["SESSION_COOKIE_SAMESITE"] = "None"  # 웹뷰에서 쿠키 공유
app.config["SESSION_COOKIE_SECURE"] = False  # 개발 환경 (HTTPS 사용 시 True)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)
```

### 2. CORS 설정

모바일 앱에서 웹뷰로 접근할 수 있도록 CORS가 설정되어 있습니다.

### 3. 환경 변수

개발 환경에서는 `SESSION_COOKIE_SECURE=False`로 설정하세요.
프로덕션(HTTPS)에서는 `SESSION_COOKIE_SECURE=True`로 설정하세요.

## 📲 모바일 앱 구현 방법

### iOS (Swift)

#### 1. WebView 설정

```swift
import SwiftUI
import WebKit

struct WebView: UIViewRepresentable {
    let url: URL
    
    func makeUIView(context: Context) -> WKWebView {
        let webView = WKWebView()
        
        // 쿠키 및 세션 지원
        let config = WKWebViewConfiguration()
        config.websiteDataStore = WKWebsiteDataStore.default()
        
        // 쿠키 공유 활성화
        let preferences = WKWebpagePreferences()
        preferences.allowsContentJavaScript = true
        config.defaultWebpagePreferences = preferences
        
        let wkWebView = WKWebView(frame: .zero, configuration: config)
        wkWebView.navigationDelegate = context.coordinator
        
        return wkWebView
    }
    
    func updateUIView(_ webView: WKWebView, context: Context) {
        let request = URLRequest(url: url)
        webView.load(request)
    }
    
    func makeCoordinator() -> Coordinator {
        Coordinator()
    }
    
    class Coordinator: NSObject, WKNavigationDelegate {
        func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            // 로그인 성공 후 리다이렉트 처리
            if let url = navigationAction.request.url {
                if url.absoluteString.contains("/upload") {
                    // 로그인 성공, 앱의 메인 화면으로 이동
                    NotificationCenter.default.post(name: NSNotification.Name("LoginSuccess"), object: nil)
                }
            }
            decisionHandler(.allow)
        }
    }
}

// 사용 예시
struct LoginView: View {
    var body: some View {
        WebView(url: URL(string: "https://your-domain.com/login")!)
    }
}
```

#### 2. 딥링크 처리 (선택사항)

`Info.plist`에 URL Scheme 추가:

```xml
<key>CFBundleURLTypes</key>
<array>
    <dict>
        <key>CFBundleURLSchemes</key>
        <array>
            <string>mozik</string>
        </array>
    </dict>
</array>
```

### Android (Kotlin)

#### 1. WebView 설정

```kotlin
import android.webkit.CookieManager
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.viewinterop.AndroidView

@Composable
fun WebViewScreen(url: String) {
    AndroidView(
        factory = { context ->
            WebView(context).apply {
                settings.javaScriptEnabled = true
                settings.domStorageEnabled = true
                settings.setSupportMultipleWindows(true)
                
                // 쿠키 활성화
                CookieManager.getInstance().setAcceptCookie(true)
                CookieManager.getInstance().setAcceptThirdPartyCookies(this, true)
                
                webViewClient = object : WebViewClient() {
                    override fun shouldOverrideUrlLoading(view: WebView?, url: String?): Boolean {
                        // 로그인 성공 후 리다이렉트 처리
                        if (url?.contains("/upload") == true) {
                            // 로그인 성공, 앱의 메인 화면으로 이동
                            // 예: viewModel.onLoginSuccess()
                        }
                        return false
                    }
                }
                
                loadUrl(url)
            }
        },
        modifier = Modifier.fillMaxSize()
    )
}

// 사용 예시
@Composable
fun LoginScreen() {
    WebViewScreen("https://your-domain.com/login")
}
```

#### 2. AndroidManifest.xml 설정

```xml
<activity
    android:name=".MainActivity"
    android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data android:scheme="mozik" />
    </intent-filter>
</activity>
```

### React Native

#### 1. react-native-webview 설치

```bash
npm install react-native-webview
```

#### 2. WebView 컴포넌트

```javascript
import React, { useRef } from 'react';
import { WebView } from 'react-native-webview';

const LoginWebView = ({ onLoginSuccess }) => {
  const webViewRef = useRef(null);

  const handleNavigationStateChange = (navState) => {
    // 로그인 성공 후 리다이렉트 처리
    if (navState.url.includes('/upload')) {
      onLoginSuccess();
    }
  };

  return (
    <WebView
      ref={webViewRef}
      source={{ uri: 'https://your-domain.com/login' }}
      onNavigationStateChange={handleNavigationStateChange}
      // 쿠키 및 세션 지원
      sharedCookiesEnabled={true}
      thirdPartyCookiesEnabled={true}
      // JavaScript 활성화
      javaScriptEnabled={true}
      domStorageEnabled={true}
    />
  );
};

export default LoginWebView;
```

### Flutter

#### 1. webview_flutter 패키지 설치

```yaml
dependencies:
  webview_flutter: ^4.0.0
```

#### 2. WebView 위젯

```dart
import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

class LoginWebView extends StatefulWidget {
  final Function() onLoginSuccess;

  const LoginWebView({Key? key, required this.onLoginSuccess}) : super(key: key);

  @override
  State<LoginWebView> createState() => _LoginWebViewState();
}

class _LoginWebViewState extends State<LoginWebView> {
  late final WebViewController _controller;

  @override
  void initState() {
    super.initState();
    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setNavigationDelegate(
        NavigationDelegate(
          onPageFinished: (String url) {
            // 로그인 성공 후 리다이렉트 처리
            if (url.contains('/upload')) {
              widget.onLoginSuccess();
            }
          },
        ),
      )
      ..loadRequest(Uri.parse('https://your-domain.com/login'));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: WebViewWidget(controller: _controller),
    );
  }
}
```

## 🔗 딥링크 설정 (선택사항)

앱에서 특정 URL을 열 때 앱 내 웹뷰로 열리도록 설정할 수 있습니다.

### Flask 앱에 딥링크 엔드포인트 추가

```python
@app.route("/app/login")
def app_login():
    """앱에서 로그인 페이지로 이동"""
    return redirect(url_for("login"))

@app.route("/app/signup")
def app_signup():
    """앱에서 회원가입 페이지로 이동"""
    return redirect(url_for("signup"))
```

## 📝 체크리스트

### Flask 앱
- [x] 세션 쿠키 설정 (SAMESITE=None)
- [x] CORS 설정
- [x] HTTPS 설정 (프로덕션)

### 모바일 앱
- [ ] WebView 컴포넌트 구현
- [ ] 쿠키/세션 지원 활성화
- [ ] 로그인 성공 후 리다이렉트 처리
- [ ] 딥링크 설정 (선택사항)

## 🚀 테스트 방법

1. **로컬 테스트**: 
   - Flask 앱을 `0.0.0.0`으로 실행
   - 모바일 기기와 같은 네트워크에서 `http://서버IP:5000` 접근

2. **프로덕션 테스트**:
   - HTTPS 도메인으로 접근
   - `SESSION_COOKIE_SECURE=True` 설정 확인

## ⚠️ 주의사항

1. **보안**: 프로덕션에서는 반드시 HTTPS를 사용하고 `SESSION_COOKIE_SECURE=True`로 설정하세요.

2. **쿠키 도메인**: `SESSION_COOKIE_DOMAIN`을 적절히 설정하여 쿠키가 정상적으로 공유되도록 하세요.

3. **CORS**: 프로덕션에서는 `origins`를 특정 도메인으로 제한하세요.

4. **세션 만료**: 모바일 앱에서도 세션 만료를 처리하도록 구현하세요.

## 📞 지원

문제가 발생하면 다음을 확인하세요:
- 웹뷰에서 쿠키가 활성화되어 있는지
- HTTPS 사용 여부와 `SESSION_COOKIE_SECURE` 설정 일치 여부
- CORS 설정이 올바른지



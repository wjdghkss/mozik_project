# Mozik 프로젝트 모바일 앱 연동 실전 가이드

이 문서는 Mozik 웹 앱에 모바일 앱을 실제로 연동하는 방법을 단계별로 설명합니다.

## 🎯 목표

- 모바일 앱에서 웹뷰로 로그인/회원가입 페이지 열기
- 로그인 성공 후 앱의 메인 화면으로 이동
- 웹 세션이 앱에서도 유지되도록 설정

## 📋 사전 준비

### 1. Flask 앱 확인
- ✅ `app.py`에 세션 쿠키 설정 완료
- ✅ CORS 설정 완료
- ✅ `flask-cors` 패키지 설치 필요

```bash
pip install flask-cors
```

### 2. 서버 URL 확인
- 개발 환경: `http://서버IP:5000`
- 프로덕션: `https://your-domain.com`

## 📱 방법 1: React Native (가장 추천)

### Step 1: 프로젝트 생성

```bash
# React Native 프로젝트 생성
npx react-native init MozikMobile

# 프로젝트 폴더로 이동
cd MozikMobile
```

### Step 2: 필요한 패키지 설치

```bash
# WebView 패키지
npm install react-native-webview

# 네비게이션 (화면 전환용)
npm install @react-navigation/native @react-navigation/native-stack
npm install react-native-screens react-native-safe-area-context
```

### Step 3: 앱 구조 만들기

프로젝트 폴더 구조:
```
MozikMobile/
├── src/
│   ├── screens/
│   │   ├── LoginScreen.js      # 로그인 웹뷰
│   │   ├── SignupScreen.js     # 회원가입 웹뷰
│   │   └── MainScreen.js       # 메인 화면 (로그인 후)
│   └── App.js                  # 메인 앱 파일
```

### Step 4: LoginScreen.js 만들기

`src/screens/LoginScreen.js` 파일 생성:

```javascript
import React, { useRef } from 'react';
import { View, StyleSheet, ActivityIndicator } from 'react-native';
import { WebView } from 'react-native-webview';

const LoginScreen = ({ onLoginSuccess }) => {
  const webViewRef = useRef(null);
  
  // 서버 URL (개발 환경에서는 실제 서버 IP로 변경)
  const SERVER_URL = 'http://192.168.0.100:5000'; // 본인의 서버 IP로 변경
  
  const handleNavigationStateChange = (navState) => {
    const url = navState.url;
    
    // 로그인 성공 후 /upload로 리다이렉트되면 성공으로 판단
    if (url.includes('/upload')) {
      console.log('로그인 성공!');
      onLoginSuccess();
    }
    
    // 회원가입 성공 후 /login으로 리다이렉트되면 회원가입 성공
    if (url.includes('/login') && navState.canGoBack) {
      console.log('회원가입 완료, 로그인 페이지로 이동');
    }
  };

  return (
    <View style={styles.container}>
      <WebView
        ref={webViewRef}
        source={{ uri: `${SERVER_URL}/login` }}
        style={styles.webview}
        onNavigationStateChange={handleNavigationStateChange}
        // 쿠키 및 세션 지원
        sharedCookiesEnabled={true}
        thirdPartyCookiesEnabled={true}
        // JavaScript 활성화
        javaScriptEnabled={true}
        domStorageEnabled={true}
        // 로딩 인디케이터
        startInLoadingState={true}
        renderLoading={() => (
          <View style={styles.loadingContainer}>
            <ActivityIndicator size="large" color="#6366f1" />
          </View>
        )}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  webview: {
    flex: 1,
  },
  loadingContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#ffffff',
  },
});

export default LoginScreen;
```

### Step 5: SignupScreen.js 만들기

`src/screens/SignupScreen.js` 파일 생성:

```javascript
import React from 'react';
import { View, StyleSheet } from 'react-native';
import { WebView } from 'react-native-webview';

const SignupScreen = ({ onSignupSuccess }) => {
  const SERVER_URL = 'http://192.168.0.100:5000'; // 본인의 서버 IP로 변경

  const handleNavigationStateChange = (navState) => {
    // 회원가입 성공 후 /login으로 리다이렉트
    if (navState.url.includes('/login')) {
      console.log('회원가입 완료');
      onSignupSuccess();
    }
  };

  return (
    <View style={styles.container}>
      <WebView
        source={{ uri: `${SERVER_URL}/signup` }}
        style={styles.webview}
        onNavigationStateChange={handleNavigationStateChange}
        sharedCookiesEnabled={true}
        thirdPartyCookiesEnabled={true}
        javaScriptEnabled={true}
        domStorageEnabled={true}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  webview: {
    flex: 1,
  },
});

export default SignupScreen;
```

### Step 6: MainScreen.js 만들기

`src/screens/MainScreen.js` 파일 생성:

```javascript
import React from 'react';
import { View, Text, StyleSheet, Button } from 'react-native';

const MainScreen = ({ onLogout }) => {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Mozik에 오신 것을 환영합니다!</Text>
      <Text style={styles.subtitle}>모자이크 처리를 시작하세요</Text>
      
      <Button
        title="로그아웃"
        onPress={onLogout}
        color="#6366f1"
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#ffffff',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#1f2937',
  },
  subtitle: {
    fontSize: 16,
    color: '#6b7280',
    marginBottom: 30,
  },
});

export default MainScreen;
```

### Step 7: App.js 수정

`App.js` 파일 수정:

```javascript
import React, { useState, useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import AsyncStorage from '@react-native-async-storage/async-storage';

import LoginScreen from './src/screens/LoginScreen';
import SignupScreen from './src/screens/SignupScreen';
import MainScreen from './src/screens/MainScreen';

const Stack = createNativeStackNavigator();

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // 앱 시작 시 로그인 상태 확인
  useEffect(() => {
    checkLoginStatus();
  }, []);

  const checkLoginStatus = async () => {
    try {
      const loginStatus = await AsyncStorage.getItem('isLoggedIn');
      if (loginStatus === 'true') {
        setIsLoggedIn(true);
      }
    } catch (error) {
      console.error('로그인 상태 확인 실패:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoginSuccess = async () => {
    try {
      await AsyncStorage.setItem('isLoggedIn', 'true');
      setIsLoggedIn(true);
    } catch (error) {
      console.error('로그인 상태 저장 실패:', error);
    }
  };

  const handleSignupSuccess = () => {
    // 회원가입 성공 시 로그인 화면으로 이동
    // (실제로는 자동 로그인 처리하거나 로그인 화면 유지)
  };

  const handleLogout = async () => {
    try {
      await AsyncStorage.removeItem('isLoggedIn');
      setIsLoggedIn(false);
    } catch (error) {
      console.error('로그아웃 실패:', error);
    }
  };

  if (isLoading) {
    return null; // 또는 로딩 화면
  }

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {!isLoggedIn ? (
          <>
            <Stack.Screen name="Login">
              {props => <LoginScreen {...props} onLoginSuccess={handleLoginSuccess} />}
            </Stack.Screen>
            <Stack.Screen name="Signup">
              {props => <SignupScreen {...props} onSignupSuccess={handleSignupSuccess} />}
            </Stack.Screen>
          </>
        ) : (
          <Stack.Screen name="Main">
            {props => <MainScreen {...props} onLogout={handleLogout} />}
          </Stack.Screen>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}

export default App;
```

### Step 8: 추가 패키지 설치

```bash
# AsyncStorage (로그인 상태 저장용)
npm install @react-native-async-storage/async-storage

# iOS에서 pod 설치 (Mac만)
cd ios && pod install && cd ..
```

### Step 9: 앱 실행

```bash
# Android 실행
npx react-native run-android

# iOS 실행 (Mac만)
npx react-native run-ios
```

## 📱 방법 2: Flutter (대안)

### Step 1: 프로젝트 생성

```bash
flutter create mozik_mobile
cd mozik_mobile
```

### Step 2: webview_flutter 패키지 추가

`pubspec.yaml` 파일에 추가:
```yaml
dependencies:
  webview_flutter: ^4.0.0
```

설치:
```bash
flutter pub get
```

### Step 3: 로그인 화면 만들기

`lib/screens/login_screen.dart` 파일 생성:

```dart
import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

class LoginScreen extends StatefulWidget {
  final Function() onLoginSuccess;

  const LoginScreen({Key? key, required this.onLoginSuccess}) : super(key: key);

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  late final WebViewController _controller;
  final String SERVER_URL = 'http://192.168.0.100:5000'; // 본인의 서버 IP로 변경

  @override
  void initState() {
    super.initState();
    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setNavigationDelegate(
        NavigationDelegate(
          onPageFinished: (String url) {
            // 로그인 성공 후 /upload로 리다이렉트되면 성공으로 판단
            if (url.contains('/upload')) {
              widget.onLoginSuccess();
            }
          },
        ),
      )
      ..loadRequest(Uri.parse('$SERVER_URL/login'));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: WebViewWidget(controller: _controller),
    );
  }
}
```

### Step 4: 메인 앱 파일

`lib/main.dart` 파일 수정:

```dart
import 'package:flutter/material.dart';
import 'screens/login_screen.dart';
import 'screens/main_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Mozik',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const AuthWrapper(),
    );
  }
}

class AuthWrapper extends StatefulWidget {
  const AuthWrapper({Key? key}) : super(key: key);

  @override
  State<AuthWrapper> createState() => _AuthWrapperState();
}

class _AuthWrapperState extends State<AuthWrapper> {
  bool _isLoggedIn = false;

  void _handleLoginSuccess() {
    setState(() {
      _isLoggedIn = true;
    });
  }

  void _handleLogout() {
    setState(() {
      _isLoggedIn = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoggedIn) {
      return MainScreen(onLogout: _handleLogout);
    } else {
      return LoginScreen(onLoginSuccess: _handleLoginSuccess);
    }
  }
}
```

## 🔧 서버 설정 확인

### 1. Flask 앱 실행 확인

```bash
# 개발 환경에서 실행
python app.py

# 또는 gunicorn으로 실행
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 2. 방화벽 확인

모바일 기기에서 서버에 접근하려면:
- 서버의 방화벽에서 5000 포트 열기
- 같은 네트워크(Wi-Fi)에 연결되어 있어야 함

### 3. 서버 IP 확인

```bash
# Linux/Mac
ifconfig

# Windows
ipconfig
```

예: `192.168.0.100` 같은 IP 주소를 앱의 `SERVER_URL`에 입력

## 🧪 테스트 방법

### 1. 개발 환경 테스트

1. Flask 서버 실행: `python app.py`
2. 서버 IP 확인: `192.168.0.100` (예시)
3. 앱의 `SERVER_URL`을 실제 서버 IP로 변경
4. 모바일 기기와 서버가 같은 Wi-Fi에 연결
5. 앱 실행 후 로그인 테스트

### 2. 프로덕션 환경

1. HTTPS 도메인 사용: `https://your-domain.com`
2. `SESSION_COOKIE_SECURE=True` 설정
3. 앱의 `SERVER_URL`을 실제 도메인으로 변경

## ⚠️ 주의사항

1. **개발 환경**: `SESSION_COOKIE_SECURE=False` (HTTP 사용 시)
2. **프로덕션**: `SESSION_COOKIE_SECURE=True` (HTTPS 필수)
3. **서버 IP 변경**: 앱을 배포할 때마다 `SERVER_URL` 확인
4. **쿠키 공유**: WebView에서 쿠키가 활성화되어 있는지 확인

## 🐛 문제 해결

### 문제 1: 로그인이 안 됨
- WebView에서 쿠키가 활성화되어 있는지 확인
- 서버 URL이 정확한지 확인
- 같은 네트워크에 연결되어 있는지 확인

### 문제 2: 세션이 유지되지 않음
- `SESSION_COOKIE_SAMESITE="None"` 설정 확인
- HTTPS 사용 시 `SESSION_COOKIE_SECURE=True` 확인

### 문제 3: CORS 오류
- `flask-cors` 패키지 설치 확인
- `CORS(app, supports_credentials=True)` 설정 확인

## 📝 체크리스트

- [ ] Flask 앱에 세션 쿠키 설정 완료
- [ ] `flask-cors` 패키지 설치
- [ ] 모바일 앱 프로젝트 생성
- [ ] WebView로 로그인 페이지 표시
- [ ] 로그인 성공 감지 구현
- [ ] 서버 IP/도메인 설정
- [ ] 테스트 완료

## 🚀 다음 단계

1. 기본 로그인/회원가입 연동 완료
2. 업로드 기능을 앱에 추가 (선택사항)
3. 작업 기록을 앱에서 확인 (선택사항)
4. 앱스토어/플레이스토어 배포 준비

이제 실제로 모바일 앱을 만들고 Mozik 웹 앱과 연동할 수 있습니다!



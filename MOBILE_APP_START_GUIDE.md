# 모바일 앱 개발 시작 가이드 (초보자용)

모바일 앱 개발이 처음이신가요? 이 가이드를 따라 단계별로 준비하세요.

## 📱 1단계: 어떤 플랫폼을 만들지 결정하기

### 옵션 1: iOS 앱 (iPhone/iPad)
- **언어**: Swift
- **도구**: Xcode (Mac 전용)
- **필요한 것**: Mac 컴퓨터 필수
- **장점**: 한 플랫폼만 집중 가능, 수익화 용이

### 옵션 2: Android 앱
- **언어**: Kotlin 또는 Java
- **도구**: Android Studio
- **필요한 것**: Windows/Mac/Linux 모두 가능
- **장점**: 다양한 기기 지원, 무료 개발

### 옵션 3: 크로스 플랫폼 (iOS + Android 동시)
- **React Native**: JavaScript로 iOS/Android 동시 개발
- **Flutter**: Dart 언어로 iOS/Android 동시 개발
- **장점**: 하나의 코드로 두 플랫폼 모두 지원

## 🎯 추천: React Native (초보자에게 가장 쉬움)

**이유:**
- JavaScript만 알면 됨 (웹 개발 경험이 있다면 더 쉬움)
- iOS와 Android를 동시에 만들 수 있음
- 웹뷰 연동이 간단함
- 커뮤니티가 크고 자료가 많음

## 🛠️ 2단계: 개발 환경 준비하기

### React Native로 시작하는 경우

#### 1. Node.js 설치
1. https://nodejs.org 접속
2. LTS 버전 다운로드 및 설치
3. 터미널에서 확인:
   ```bash
   node --version
   npm --version
   ```

#### 2. React Native CLI 설치
```bash
npm install -g react-native-cli
```

#### 3. Android 개발 환경 (Android 앱을 만들 경우)
- **Android Studio 설치**: https://developer.android.com/studio
- 설치 후 Android SDK 자동 설치됨
- 에뮬레이터(가상 기기) 설정

#### 4. iOS 개발 환경 (iOS 앱을 만들 경우)
- **Xcode 설치**: Mac App Store에서 "Xcode" 검색 후 설치
- 설치 후 Command Line Tools 자동 설치됨
- 시뮬레이터(가상 기기) 사용 가능

### iOS만 만들 경우 (Swift)

#### 1. Mac 컴퓨터 필요
- iOS 앱은 Mac에서만 개발 가능

#### 2. Xcode 설치
- Mac App Store에서 "Xcode" 검색 후 설치 (약 10GB)
- 설치 시간: 1-2시간 소요

#### 3. Apple Developer 계정 (선택사항)
- 무료 계정으로도 개발 가능
- 앱스토어 배포 시 유료 계정 필요 ($99/년)

### Android만 만들 경우 (Kotlin)

#### 1. Android Studio 설치
- https://developer.android.com/studio 접속
- 운영체제에 맞는 버전 다운로드
- 설치 마법사 따라하기

#### 2. Android SDK 설정
- Android Studio 실행 후 SDK Manager에서 최신 SDK 설치

## 📚 3단계: 기본 학습하기

### React Native 학습 경로 (추천)

#### 1주차: JavaScript 기초
- 변수, 함수, 객체, 배열
- 비동기 처리 (Promise, async/await)
- 온라인 강의: YouTube "JavaScript 기초"

#### 2주차: React 기초
- 컴포넌트 개념
- Props와 State
- 온라인 강의: React 공식 문서 또는 YouTube

#### 3주차: React Native 시작
- 공식 문서: https://reactnative.dev/docs/getting-started
- 첫 앱 만들기: "Hello World"
- 온라인 강의: YouTube "React Native 튜토리얼"

#### 4주차: WebView 연동
- react-native-webview 패키지 사용
- 웹 페이지를 앱에 표시하기

### Swift (iOS) 학습 경로

#### 1주차: Swift 기초
- 변수, 함수, 클래스
- Swift 공식 문서: https://docs.swift.org/swift-book/

#### 2주차: iOS 앱 구조 이해
- Xcode 프로젝트 구조
- Storyboard 또는 SwiftUI

#### 3주차: 첫 앱 만들기
- "Hello World" 앱
- 버튼 클릭 이벤트

#### 4주차: WebView 연동
- WKWebView 사용법

### Kotlin (Android) 학습 경로

#### 1주차: Kotlin 기초
- 변수, 함수, 클래스
- Kotlin 공식 문서: https://kotlinlang.org/docs/home.html

#### 2주차: Android 앱 구조
- Activity, Fragment 개념
- Layout XML

#### 3주차: 첫 앱 만들기
- "Hello World" 앱
- 버튼 클릭 이벤트

#### 4주차: WebView 연동
- WebView 컴포넌트 사용

## 🚀 4단계: 실제 프로젝트 시작하기

### React Native 프로젝트 생성

```bash
# 새 프로젝트 생성
npx react-native init MozikApp

# 프로젝트 폴더로 이동
cd MozikApp

# iOS 실행 (Mac만 가능)
npx react-native run-ios

# Android 실행
npx react-native run-android
```

### 첫 WebView 화면 만들기

1. **react-native-webview 설치**
   ```bash
   npm install react-native-webview
   ```

2. **LoginScreen.js 파일 생성**
   ```javascript
   import React from 'react';
   import { View, StyleSheet } from 'react-native';
   import { WebView } from 'react-native-webview';

   const LoginScreen = () => {
     return (
       <View style={styles.container}>
         <WebView
           source={{ uri: 'https://your-domain.com/login' }}
           style={styles.webview}
           sharedCookiesEnabled={true}
           thirdPartyCookiesEnabled={true}
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

   export default LoginScreen;
   ```

3. **App.js에서 사용**
   ```javascript
   import LoginScreen from './LoginScreen';

   function App() {
     return <LoginScreen />;
   }
   ```

## 📖 학습 자료 추천

### 무료 강의
- **YouTube**: "React Native 튜토리얼", "iOS 앱 개발", "Android 앱 개발"
- **공식 문서**: 각 플랫폼 공식 문서 (가장 정확함)
- **Stack Overflow**: 문제 해결

### 유료 강의 (선택사항)
- **Udemy**: "React Native 완전정복"
- **인프런**: 한국어 강의 많음
- **Nomad Coders**: 무료/유료 혼합

## ⚠️ 초보자가 자주 하는 실수

1. **너무 많은 것을 한 번에 배우려고 함**
   - 하나씩 차근차근 배우세요
   - 기본부터 확실히 이해하기

2. **에러 메시지를 무시함**
   - 에러 메시지를 읽고 이해하려고 노력하세요
   - 구글에 에러 메시지를 검색하면 해결책을 찾을 수 있어요

3. **최신 버전만 사용하려고 함**
   - 튜토리얼은 보통 특정 버전 기준
   - 튜토리얼과 같은 버전 사용 권장

## 🎯 단계별 체크리스트

### 준비 단계
- [ ] 플랫폼 선택 (iOS/Android/둘 다)
- [ ] 개발 도구 설치 완료
- [ ] 첫 "Hello World" 앱 실행 성공

### 학습 단계
- [ ] 기본 문법 이해
- [ ] 간단한 앱 만들기 (계산기, 할 일 목록 등)
- [ ] WebView 사용법 이해

### 프로젝트 단계
- [ ] Mozik 앱 프로젝트 생성
- [ ] WebView로 로그인 페이지 표시
- [ ] 로그인 성공 후 처리

## 💡 팁

1. **작은 것부터 시작**: 복잡한 기능보다 간단한 것부터
2. **공식 문서 활용**: 가장 정확한 정보
3. **커뮤니티 참여**: 질문하고 답변 받기
4. **실습 위주**: 이론보다 직접 만들어보기

## 🆘 도움이 필요할 때

1. **공식 문서**: 가장 먼저 확인
2. **Stack Overflow**: 에러 메시지 검색
3. **GitHub Issues**: 비슷한 문제 찾기
4. **커뮤니티**: Reddit, Discord 등

## 📝 다음 단계

1. 이 가이드대로 개발 환경 준비
2. 기본 튜토리얼 따라하기
3. 간단한 앱 하나 만들어보기
4. `MOBILE_APP_INTEGRATION.md` 파일의 코드 참고하여 Mozik 앱 연동

**중요**: 처음에는 어려울 수 있지만, 하나씩 배워가면 됩니다. 포기하지 마세요! 🚀



# Android Keystore & Signed AAB Build Guide

This document specifies the procedure for building and signing the Android App Bundle (AAB) for Google Play release (`ANDR-01`, `ANDR-02`, `ANDR-03`).

---

### 1. Keystore Generation
Generate a dedicated release keystore:
```bash
keytool -genkey -v -keystore smokerkhata-release-key.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias smokerkhata-key
```

### 2. Gradle Signing Configuration (`android/app/build.gradle`)
Add release signing credentials:
```groovy
android {
    ...
    defaultConfig {
        applicationId "com.smokerkhata.app"
        minSdkVersion 22
        targetSdkVersion 34
        versionCode 1
        versionName "1.0.0"
    }

    signingConfigs {
        release {
            storeFile file(System.getenv("KEYSTORE_PATH") ?: "smokerkhata-release-key.jks")
            storePassword System.getenv("KEYSTORE_PASSWORD")
            keyAlias System.getenv("KEY_ALIAS") ?: "smokerkhata-key"
            keyPassword System.getenv("KEY_PASSWORD")
        }
    }

    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}
```

### 3. Generate Signed Android App Bundle (AAB)
```bash
cd android
./gradlew bundleRelease
```
The generated bundle will be located at:
`android/app/build/outputs/bundle/release/app-release.aab`

### 4. Google Play Billing Plugin Integration (`ANDR-03`)
In `package.json`:
- Integrate `@capgo/capacitor-purchases` or official Play Billing Capacitor plugin.
- On client purchase success, forward purchase token to `POST /api/subscriptions/play-billing/verify/` for server-side authorization.

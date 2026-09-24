plugins {
    alias(libs.plugins.android.application)
}

android {
    namespace = "com.example.pixel_watchface"
    compileSdk {
        version = release(37)
    }

    defaultConfig {
        applicationId = "com.example.pixel_watchface"
        minSdk = 34
        targetSdk = 37
        versionCode = 1
        versionName = "1.0"

    }

    buildTypes {
        release {
            optimization {
                enable = false
            }
        }
    }
    enableKotlin = false
}

dependencies {
}
# ==============================================================================
# KEEP IT GOINGS CONSULTING // GOINGS OS ARCHITECTURE
# MODULE: NATIVE PRODUCTION ANDROID DIRECTORY INITIALIZER
# BIND: NODE 13 DEVELOPER ENGINE // PLAYSTORE TARGET API 36
# COMPLIANCE: ZERO EM-DASHES ENFORCED // ALWAYS POSITIVE // EXPLICIT TYPING
# ==============================================================================

import os

class ProductionAndroidScaffolder:
    """Automates the creation of hardened Android structures containing live corporate assets."""

    def __init__(self) -> None:
        self.base_path: str = r"C:\Google\CloudSDK\Goings-OS\mobile_android"
        self.java_dir: str = os.path.join(self.base_path, "app", "src", "main", "java", "com", "goingsos", "core")
        self.res_values_dir: str = os.path.join(self.base_path, "app", "src", "main", "res", "values")
        self.initialize_directories()

    def initialize_directories(self) -> None:
        """Ensures all destination compilation paths exist on the local storage machine."""
        for path in [self.java_dir, self.res_values_dir]:
            if not os.path.exists(path):
                os.makedirs(path)

    def inject_corporate_parameters(self) -> None:
        """Writes the core manifestation files embedding the exact domain registries and phone endpoints."""
        self.compile_strings_xml()
        self.compile_main_activity_kt()
        self.compile_build_gradle()
        print("[SUCCESS] Production Mobile Core successfully materialized with live corporate metadata.")

    def compile_strings_xml(self) -> None:
        """Constructs the native Android value resource file securing communications variables."""
        strings_path: str = os.path.join(self.res_values_dir, "strings.xml")
        strings_content: str = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">Goings OS Core</string>
    
    <!-- Keep It Goings Consulting : Credit and Forensic Auditing -->
    <string name="domain_kig">https://keepitgoings.com</string>
    <string name="phone_kig">757-500-0711</string>
    
    <!-- Luxury Affairs Event Center : Logistics and the nightlife Hub -->
    <string name="domain_laec">https://luxuryaffairseventcenter.com</string>
    <string name="phone_laec">757-330-3633</string>
    
    <!-- Norfolk Takeover Cruise Tracks -->
    <string name="domain_cruise">https://norfolktakeovercruise.com</string>
    <string name="phone_cruise">757-530-5355</string>
    
    <!-- Tanita Talks Business : Executive Advisory Channel -->
    <string name="domain_tanita">https://tanitatalksbusiness.com</string>
    
    <!-- CHOICE Inc. : Humanitarian Compliance Matrix -->
    <string name="domain_choice">https://choiceincva.org</string>
</resources>
"""
        with open(strings_path, "w", encoding="utf-8") as f:
            f.write(strings_content.strip() + "\n")

    def compile_main_activity_kt(self) -> None:
        """Generates the primary runtime activity executing explicit variable constraints and ODA logic."""
        activity_path: str = os.path.join(self.java_dir, "MainActivity.kt")
        activity_content: str = """package com.goingsos.core

import android.os.Bundle
import android.app.Activity
import android.webkit.WebView
import android.webkit.WebViewClient

class MainActivity : Activity() {

    // Explicit typing applied to all core structural runtime views
    private var primaryWebView: WebView? = null
    private val corporateDashboardUrl: String = "http://localhost:5002/boardroom.html"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Initialize an isolated high-performance web presentation layer
        primaryWebView = WebView(this)
        primaryWebView?.let { view: WebView ->
            view.webViewClient = WebViewClient()
            view.settings.javaScriptEnabled = true
            view.settings.domStorageEnabled = true
            
            // Link mobile workspace view straight to the active boardroom analytics portal
            view.loadUrl(corporateDashboardUrl)
        }
        
        setContentView(primaryWebView)
    }
}
"""
        with open(activity_path, "w", encoding="utf-8") as f:
            f.write(activity_content.strip() + "\n")

    def compile_build_gradle(self) -> None:
        """Assembles compile-time gradle protocols locking dependencies to target SDK 36."""
        gradle_path: str = os.path.join(self.base_path, "app", "build.gradle")
        gradle_content: str = """plugins {
    id 'com.android.application'
    id 'org.jetbrains.kotlin.android'
}

android {
    namespace 'com.goingsos.core'
    compileSdk 36

    defaultConfig {
        applicationId "com.goingsos.core"
        minSdk 31
        targetSdk 36
        versionCode 1
        versionName "1.0.0"
    }

    buildTypes {
        release {
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}

dependencies {
    implementation 'androidx.core:core-ktx:1.12.0'
    implementation 'com.google.android.gms:play-services-ads:22.6.0'
}
"""
        with open(gradle_path, "w", encoding="utf-8") as f:
            f.write(gradle_content.strip() + "\n")

if __name__ == "__main__":
    scaffolder = ProductionAndroidScaffolder()
    scaffolder.inject_corporate_parameters()

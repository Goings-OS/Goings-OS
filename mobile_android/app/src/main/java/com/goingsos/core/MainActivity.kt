package com.goingsos.core

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

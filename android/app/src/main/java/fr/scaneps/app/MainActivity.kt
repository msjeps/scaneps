package fr.scaneps.app

import android.Manifest
import android.annotation.SuppressLint
import android.app.Activity
import android.content.pm.ActivityInfo
import android.content.pm.PackageManager
import android.os.Bundle
import android.view.WindowManager
import android.webkit.JavascriptInterface
import android.webkit.PermissionRequest
import android.webkit.WebResourceRequest
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebChromeClient
import android.webkit.WebViewClient
import androidx.activity.OnBackPressedCallback
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import androidx.webkit.ServiceWorkerClientCompat
import androidx.webkit.ServiceWorkerControllerCompat
import androidx.webkit.WebSettingsCompat
import androidx.webkit.WebViewAssetLoader
import androidx.webkit.WebViewFeature
import java.io.IOException
import java.io.OutputStreamWriter
import org.json.JSONObject

class MainActivity : AppCompatActivity() {

    companion object {
        private const val APP_HOST = "appassets.androidplatform.net"
    }

    private lateinit var webView: WebView
    private var pendingPermissionRequest: PermissionRequest? = null

    // Données CSV en attente d'écriture (après sélection du dossier)
    private var pendingCsvContent: String = ""
    private var pendingCsvFilename: String = ""

    // Lanceur de demande de permission caméra (runtime)
    private val cameraLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        pendingPermissionRequest?.let { req ->
            if (isGranted) req.grant(req.resources) else req.deny()
            pendingPermissionRequest = null
        }
    }

    // Signale un résultat à la page via updateStatut (message passé par JSONObject.quote)
    private fun notifierPage(texte: String, classe: String) {
        webView.post {
            webView.evaluateJavascript(
                "updateStatut(${JSONObject.quote(texte)}, ${JSONObject.quote(classe)});",
                null
            )
        }
    }

    // Lanceur pour créer/sauvegarder un fichier CSV (ouvre le sélecteur de fichier système)
    // L'utilisateur peut naviguer vers Google Drive et choisir/créer un dossier
    private val createDocumentLauncher = registerForActivityResult(
        ActivityResultContracts.CreateDocument("text/csv")
    ) { uri ->
        val contenu = pendingCsvContent
        pendingCsvContent = ""
        pendingCsvFilename = ""
        when {
            uri == null ->
                notifierPage("Export annulé : aucun fichier enregistré.", "statut-warning")
            contenu.isEmpty() ->
                notifierPage("❌ Export impossible : relance l'export.", "statut-warning")
            else -> try {
                contentResolver.openOutputStream(uri)?.use { stream ->
                    OutputStreamWriter(stream, Charsets.UTF_8).use { writer ->
                        writer.write(contenu)
                    }
                } ?: throw IOException("Fichier inaccessible")
                notifierPage("✅ Fichier CSV enregistré avec succès !", "statut-success")
            } catch (e: Exception) {
                notifierPage("❌ Erreur lors de l'enregistrement : ${e.message ?: "erreur inconnue"}", "statut-warning")
            }
        }
    }

    // Interface JavaScript exposée à la WebView sous window.Android
    inner class WebAppInterface(private val activity: Activity) {

        /** Sauvegarde un CSV via le sélecteur de fichier système (stockage local / Drive) */
        @JavascriptInterface
        fun saveCSV(content: String, filename: String) {
            if (content.length > 5_000_000) {
                notifierPage("❌ Export trop volumineux (plus de 5 Mo).", "statut-warning")
                return
            }
            // Nom assaini : pas de séparateur de chemin ni de caractère inattendu
            val safeName = filename.replace(Regex("[^A-Za-z0-9._-]"), "_").take(100)
                .ifEmpty { "export.csv" }
            pendingCsvContent = content
            pendingCsvFilename = safeName
            activity.runOnUiThread {
                createDocumentLauncher.launch(safeName)
            }
        }

        /** Ferme l'application (après confirmation dans la page) */
        @JavascriptInterface
        fun quitApp() {
            activity.runOnUiThread { activity.finish() }
        }

        /**
         * Ouvre le sélecteur de fichier système avec Google Drive comme destination.
         * L'utilisateur peut naviguer dans Drive, choisir un dossier existant
         * ou en créer un nouveau avant de valider l'enregistrement.
         */
        @JavascriptInterface
        fun openGoogleDrive(content: String, filename: String) {
            // ACTION_CREATE_DOCUMENT ouvre le sélecteur système.
            // Si Google Drive est installé, il apparaît dans la liste des destinations
            // et permet la navigation dans les dossiers et la création de nouveaux dossiers.
            saveCSV(content, filename)
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_PORTRAIT
        // L'écran ne doit pas se mettre en veille pendant une session de scan
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        setContentView(R.layout.activity_main)
        webView = findViewById(R.id.webView)
        masquerBarresSysteme()

        // Bouton retour → historique WebView
        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                // La page gère l'appui (ferme une fenêtre, ou demande confirmation si des
                // données sont scannées) ; sinon, ou si elle ne répond pas, on quitte.
                webView.evaluateJavascript(
                    "(typeof window.__androidBack === 'function') ? window.__androidBack() : false"
                ) { reponse -> if (reponse != "true") finish() }
            }
        })

        // Asset loader : sert les fichiers locaux via HTTPS (requis pour Service Worker)
        val assetLoader = WebViewAssetLoader.Builder()
            .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(this))
            .build()

        // WebViewClient : intercepte les requêtes vers les assets locaux
        webView.webViewClient = object : WebViewClient() {
            override fun shouldInterceptRequest(view: WebView, request: WebResourceRequest) =
                assetLoader.shouldInterceptRequest(request.url)

            // Le pont window.Android n'est joignable que depuis les pages de l'app
            override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean =
                request.url.host != APP_HOST
        }

        // WebChromeClient : gère la demande de permission caméra depuis le JS (getUserMedia)
        webView.webChromeClient = object : WebChromeClient() {
            override fun onPermissionRequest(request: PermissionRequest) {
                if (request.origin.host == APP_HOST &&
                    request.resources.contains(PermissionRequest.RESOURCE_VIDEO_CAPTURE)) {
                    if (ContextCompat.checkSelfPermission(
                            this@MainActivity, Manifest.permission.CAMERA
                        ) == PackageManager.PERMISSION_GRANTED
                    ) {
                        request.grant(request.resources)
                    } else {
                        pendingPermissionRequest = request
                        cameraLauncher.launch(Manifest.permission.CAMERA)
                    }
                } else {
                    request.deny()
                }
            }
        }

        // Interface JS → Android pour l'export de fichiers
        webView.addJavascriptInterface(WebAppInterface(this), "Android")

        // Configuration WebView
        with(webView.settings) {
            javaScriptEnabled                  = true
            domStorageEnabled                  = true
            allowFileAccess                    = false
            allowContentAccess                 = false
            cacheMode                          = WebSettings.LOAD_DEFAULT
            setSupportZoom(false)
            setSupportMultipleWindows(false)
            javaScriptCanOpenWindowsAutomatically = false
            mediaPlaybackRequiresUserGesture   = false
        }

        if (WebViewFeature.isFeatureSupported(WebViewFeature.SAFE_BROWSING_ENABLE)) {
            WebSettingsCompat.setSafeBrowsingEnabled(webView.settings, true)
        }

        // Service Worker : intercepte aussi via l'asset loader
        if (WebViewFeature.isFeatureSupported(WebViewFeature.SERVICE_WORKER_BASIC_USAGE)) {
            ServiceWorkerControllerCompat.getInstance()
                .setServiceWorkerClient(object : ServiceWorkerClientCompat() {
                    override fun shouldInterceptRequest(request: WebResourceRequest) =
                        assetLoader.shouldInterceptRequest(request.url)
                })
        }

        // Chargement initial ou restauration d'état
        if (savedInstanceState != null) {
            webView.restoreState(savedInstanceState)
        } else {
            webView.loadUrl("https://appassets.androidplatform.net/assets/index.html")
        }
    }

    // Plein écran immersif : barres système masquées, réaffichées un instant par un balayage du bord
    private fun masquerBarresSysteme() {
        val controleur = WindowInsetsControllerCompat(window, window.decorView)
        controleur.hide(WindowInsetsCompat.Type.systemBars())
        controleur.systemBarsBehavior =
            WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
    }

    // Les barres reviennent après le sélecteur de fichiers ou une demande de permission :
    // on les masque à nouveau dès que la fenêtre reprend le focus
    override fun onWindowFocusChanged(hasFocus: Boolean) {
        super.onWindowFocusChanged(hasFocus)
        if (hasFocus) masquerBarresSysteme()
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        webView.saveState(outState)
    }
}

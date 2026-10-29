package online.devnazu.books

import android.app.AlertDialog
import android.graphics.Color
import android.os.*
import android.view.*
import android.webkit.*
import android.widget.*
import android.speech.tts.TextToSpeech
import androidx.activity.ComponentActivity
import androidx.activity.OnBackPressedCallback
import androidx.webkit.WebViewAssetLoader
import org.json.*
import java.io.ByteArrayInputStream
import java.time.Instant
import java.util.Locale
import java.util.UUID
import java.util.concurrent.Executors

class MainActivity : ComponentActivity() {
    private lateinit var vault: TokenVault
    private lateinit var api: BooksApi
    private lateinit var ads: RewardAds
    private lateinit var root: LinearLayout
    private lateinit var area: LinearLayout
    private val worker=Executors.newFixedThreadPool(3)
    private val handler=Handler(Looper.getMainLooper())
    private var data=JSONObject()
    private var bn=true
    private var tab="Home"
    private var selected="N5"
    private var serverAt=0L
    private var elapsedAt=0L
    private var web: WebView?=null
    private var readerLevel: String?=null
    private var readerExpiry=0L
    private var status: TextView?=null
    private var tts: TextToSpeech?=null
    private val ink=Color.rgb(23,61,55)
    private val paper=Color.rgb(246,242,233)
    private val ticker=object:Runnable { override fun run(){
        if(web!=null && readerLevel!=null && now()>=readerExpiry){closeReader();message(tr("Access expired. Unused credits are safe.","সময় শেষ হয়েছে। অব্যবহৃত ক্রেডিট রাখা হয়েছে।"));refresh()}
        findViewById<TextView>(R.id.access_countdown)?.text=accessText(selected)
        handler.postDelayed(this,1000)
    }}
    override fun onCreate(savedInstanceState:Bundle?){
        super.onCreate(savedInstanceState)
        window.addFlags(WindowManager.LayoutParams.FLAG_SECURE)
        vault=TokenVault(this);api=BooksApi {vault.read()};ads=RewardAds(this)
        tts=TextToSpeech(this) { result -> if(result==TextToSpeech.SUCCESS)tts?.language=Locale.JAPANESE }
        onBackPressedDispatcher.addCallback(this,object:OnBackPressedCallback(true){override fun handleOnBackPressed(){if(web!=null)closeReader() else if(tab!="Home"){tab="Home";draw()}else finish()}})
        draw();ads.updateConsent {};handler.post(ticker)
        if(vault.read().isNotEmpty())refresh()
    }
    private fun tr(en:String,be:String)=if(bn)be else en
    private fun dp(n:Int)=(n*resources.displayMetrics.density).toInt()
    private fun text(value:String,size:Float=16f):TextView=TextView(this).apply{text=value;textSize=size;setTextColor(ink);setPadding(0,dp(6),0,dp(6))}
    private fun button(label:String,action:()->Unit):Button=Button(this).apply{text=label;isAllCaps=false;setTextColor(ink);setOnClickListener{action()}}
    private fun add(label:String,size:Float=16f){area.addView(text(label,size))}
    private fun card(action:LinearLayout.()->Unit){area.addView(LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;setPadding(dp(18),dp(14),dp(18),dp(14));background=android.graphics.drawable.GradientDrawable().apply{setColor(Color.WHITE);cornerRadius=dp(20).toFloat()};layoutParams=LinearLayout.LayoutParams(-1,-2).apply{setMargins(0,dp(8),0,dp(8))};action()})}
    private fun now()=if(serverAt==0L)System.currentTimeMillis() else serverAt+(SystemClock.elapsedRealtime()-elapsedAt)
    private fun expiry(level:String):Long {val rows=data.optJSONArray("unlocks")?:JSONArray();for(i in 0 until rows.length()){val r=rows.getJSONObject(i);if(r.optString("level")==level)return runCatching{Instant.parse(r.getString("expires_at")).toEpochMilli()}.getOrDefault(0)};return 0}
    private fun balance(level:String):Int {val rows=data.optJSONArray("balances")?:JSONArray();for(i in 0 until rows.length()){val r=rows.getJSONObject(i);if(r.optString("level")==level)return r.optInt("credits")};return 0}
    private fun accessText(level:String):String {val left=Access.remaining(expiry(level),now())/1000;return if(left<=0)tr("Locked · ${balance(level)} credits","লক করা · ${balance(level)} ক্রেডিট") else tr("Open · %dh %02dm %02ds remaining","খোলা · বাকি %d ঘণ্টা %02d মিনিট %02d সেকেন্ড").format(left/3600,left/60%60,left%60)}
    private fun message(s:String){status?.text=s;Toast.makeText(this,s,Toast.LENGTH_LONG).show()}
    private fun async(action:()->JSONObject,done:(JSONObject)->Unit){worker.execute{try{val value=action();runOnUiThread{if(!isDestroyed)done(value)}}catch(e:Exception){runOnUiThread{if(!isDestroyed){if(e is ApiError && e.code==401){vault.clear();data=JSONObject();if(web!=null)closeReader();tab="Account";draw()};message(e.message?:tr("Connection failed. Try again.","সংযোগ হয়নি। আবার চেষ্টা করুন।"))}}}}}
    private fun refresh(after:(()->Unit)?=null){if(vault.read().isEmpty())return;async({api.request("/me")}){data=it;serverAt=Instant.parse(it.getString("serverTime")).toEpochMilli();elapsedAt=SystemClock.elapsedRealtime();if(web==null)draw();after?.invoke()}}
    private fun draw(){
        if(web!=null)return
        root=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;setBackgroundColor(paper);setPadding(dp(18),dp(30),dp(18),dp(12))}
        val head=LinearLayout(this);head.addView(text("日  Nihongo Path Books",20f),LinearLayout.LayoutParams(0,-2,1f));head.addView(button(if(bn)"EN" else "বাংলা"){bn=!bn;draw()});root.addView(head)
        val scroll=ScrollView(this);area=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL};scroll.addView(area);root.addView(scroll,LinearLayout.LayoutParams(-1,0,1f))
        val nav=LinearLayout(this);listOf("Home","Rewards","Account").forEach { page->nav.addView(button(when(page){"Home"->tr("Library","বইঘর");"Rewards"->tr("Rewards","ক্রেডিট");else->tr("Account","অ্যাকাউন্ট")}){tab=page;draw()},LinearLayout.LayoutParams(0,-2,1f)) };root.addView(nav);setContentView(root)
        when(tab){"Rewards"->rewards();"Account"->account();else->home()}
        status=text("");area.addView(status)
    }
    private fun home(){
        add(tr("YOUR PERSONAL STUDY ROOM","আপনার নিজের পড়ার ঘর"),12f);add(tr("A little focus.\nA new chapter.","একটু মনোযোগ।\nনতুন একটি অধ্যায়।"),32f)
        add(tr("Read Japanese with Bengali meanings. One page at a time.","বাংলা অর্থসহ জাপানি পড়ুন। প্রতিদিন একটু করে এগিয়ে যান।"))
        card {addView(text(tr("Start here · Always free","শুরু এখানেই · সবসময় ফ্রি"),22f));addView(text(tr("Hiragana · Katakana · Japanese numbers","হিরাগানা · কাতাকানা · জাপানি সংখ্যা")));addView(button(tr("Open basics →","প্রাথমিক পাঠ খুলুন →")){openReader("basics/index.html",null)})}
        if(!api.configured)add(tr("Test build: study server not connected. Free basics work offline; secure levels need server configuration.","পরীক্ষামূলক অ্যাপ: স্টাডি সার্ভার যুক্ত হয়নি। প্রাথমিক পাঠ অফলাইনে পড়তে পারবেন; লেভেল খুলতে সার্ভার লাগবে।"))
        Access.levels.forEach {level->card {addView(text(level,30f));addView(text(accessText(level)));addView(text(tr("Vocabulary · Grammar · Kanji · Listening","শব্দভান্ডার · ব্যাকরণ · কানজি · লিসেনিং")));addView(button(tr("Explore book →","বই খুলুন →")){chooseSubject(level)})}}
        add(tr("Only existing material is included. Listening is currently supplied for N5; other listening books are not yet present in the repository.","বর্তমান বইয়ের পাঠই রাখা হয়েছে। Repository-তে এখন N5 লিসেনিং আছে; অন্য লেভেলের লিসেনিং বই এখনো নেই।"),13f)
    }
    private fun chooseSubject(level:String){selected=level
        if(vault.read().isEmpty()){tab="Account";draw();message(tr("Sign in to sync access and credits","ক্রেডিট ও পড়ার সময় সংরক্ষণ করতে লগইন করুন"));return}
        refresh {if(expiry(level)<=now()){tab="Rewards";draw()}else AlertDialog.Builder(this).setTitle(level).setItems(arrayOf(tr("Vocabulary","শব্দভান্ডার"),tr("Grammar","ব্যাকরণ"),tr("Kanji","কানজি"),tr("Listening","লিসেনিং"),tr("Original PDF book","মূল PDF বই"))){_,i->
            if(i==3)openReader("listening.html?level=$level",level) else if(i==4)openPdfBook(level) else openReader("${level.lowercase()}.html?section=${listOf("vocab","grammar","kanji")[i]}",level)
        }.show()}
    }
    private fun openPdfBook(level:String){
        if(level=="N1"){message(tr("N1 has text lessons; no owner PDF is supplied.","N1-এর পাঠ টেক্সটে আছে; মালিকের PDF দেওয়া হয়নি।"));return}
        openReader("${level.lowercase()}.html?section=vocab&edition=pdf",level)
    }
    private fun rewards(){
        add(tr("Reward Center","ক্রেডিট সেন্টার"),30f);add(tr("Choose a level. Finish an optional ad to earn one verified credit for that level. Redeem only when you choose.","লেভেল বেছে নিন। ইচ্ছামতো একটি বিজ্ঞাপন সম্পূর্ণ দেখে সেই লেভেলের একটি যাচাইকৃত ক্রেডিট পান। নিজের পছন্দে সময় কিনুন।"))
        val picker=Spinner(this);picker.adapter=ArrayAdapter(this,android.R.layout.simple_spinner_dropdown_item,Access.levels);picker.setSelection(Access.levels.indexOf(selected));area.addView(picker);picker.onItemSelectedListener=object:AdapterView.OnItemSelectedListener{override fun onNothingSelected(p:AdapterView<*>?){};override fun onItemSelected(p:AdapterView<*>?,v:View?,pos:Int,id:Long){val n=Access.levels[pos];if(n!=selected){selected=n;draw()}}}
        area.addView(text(accessText(selected),20f).apply{id=R.id.access_countdown})
        area.addView(button(tr("Watch one ad · earn 1 $selected credit","একটি বিজ্ঞাপন দেখুন · $selected-এর ১ ক্রেডিট পান")){watchAd()})
        val tiers=data.optJSONArray("tiers")?:JSONArray()
        if(tiers.length()==0){add(tr("Sign in and sync to load available unlock durations.","উপলব্ধ সময় দেখতে লগইন করে সিঙ্ক করুন।"));val costs=Access.thresholds.getValue(selected);listOf("5h","24h","3d","7d").forEachIndexed{i,s->add("$s · ${costs[i]} "+tr("credits","ক্রেডিট"))}}
        for(i in 0 until tiers.length()){val tier=tiers.getJSONObject(i);if(tier.optString("level")!=selected||!tier.optBoolean("enabled"))continue
            val duration=when(tier.getInt("seconds")){18000->tr("5 hours","৫ ঘণ্টা");86400->tr("24 hours","২৪ ঘণ্টা");259200->tr("3 days","৩ দিন");604800->tr("7 days","৭ দিন");else->"${tier.getInt("seconds")/3600} h"}
            card{addView(text("$duration · ${tier.getInt("credits")} "+tr("credits","ক্রেডিট"),21f));addView(button(tr("Redeem & start access","ক্রেডিট দিয়ে পড়া শুরু করুন")){
                AlertDialog.Builder(this@MainActivity).setTitle(tr("Unlock $selected?","$selected খুলবেন? ")).setMessage(tr("Use ${tier.getInt("credits")} credits for $duration. Access starts immediately.","${tier.getInt("credits")} ক্রেডিট দিয়ে $duration পড়ুন। এখনই সময় শুরু হবে।")).setNegativeButton(tr("Cancel","বাতিল"),null).setPositiveButton(tr("Redeem","খুলুন")){_,_->redeem(tier.getString("id"))}.show()
            }.apply{isEnabled=expiry(selected)<=now()&&balance(selected)>=tier.getInt("credits")})}
        }
        area.addView(button(tr("Refresh verification & access","যাচাই ও সময় আপডেট করুন")){refresh()})
        add(tr("Reward history","ক্রেডিটের ইতিহাস"),22f);val history=data.optJSONArray("rewards")?:JSONArray();for(i in 0 until minOf(10,history.length())){val r=history.getJSONObject(i);add("${r.optString("level")} +1 · ${r.optString("created_at")}",13f)}
        add(tr("Unlock history","সময় খোলার ইতিহাস"),22f);val red=data.optJSONArray("redemptions")?:JSONArray();for(i in 0 until minOf(10,red.length())){val r=red.getJSONObject(i);add("${r.optString("level")} −${r.optInt("credits")} · ${r.optString("expires_at")}",13f)}
    }
    private fun redeem(tier:String){
        // Keep request ID on uncertain network results; retries cannot double-spend.
        val prefs=getSharedPreferences("redemptions",MODE_PRIVATE);val key="${data.optJSONObject("user")?.optString("id")}:$tier";val id=prefs.getString(key,null)?:UUID.randomUUID().toString().also{prefs.edit().putString(key,it).apply()}
        async({api.request("/redeem","POST",JSONObject().put("tierId",tier).put("requestId",id))}){prefs.edit().remove(key).apply();message(tr("Access unlocked","পড়ার সময় খোলা হয়েছে"));refresh()}
    }
    private fun watchAd(){
        if(vault.read().isEmpty()){tab="Account";draw();return}
        val level=selected
        async({api.request("/ads/session","POST",JSONObject().put("level",level))}){s->ads.show(s.getString("id"),s.getString("userId"),{message(it)}){
            refresh();listOf(3000L,10000L,30000L).forEach{delay->handler.postDelayed({if(!isDestroyed)refresh()},delay)}
        }}
    }
    private fun field(hint:String,password:Boolean=false)=EditText(this).apply{this.hint=hint;setSingleLine();inputType=if(password)129 else 1;area.addView(this)}
    private fun account(){
        add(tr("Your study account","আপনার স্টাডি অ্যাকাউন্ট"),30f)
        if(vault.read().isEmpty()){
            val email=field(tr("Email","ইমেইল"));email.inputType=33;val password=field(tr("Password · at least 10 characters","পাসওয়ার্ড · অন্তত ১০ অক্ষর"),true);val name=field(tr("Name (new account)","নাম (নতুন অ্যাকাউন্ট)"))
            fun submit(register:Boolean){val b=JSONObject().put("email",email.text.toString()).put("password",password.text.toString()).put("name",name.text.toString());async({api.request(if(register)"/auth/register" else "/auth/login","POST",b)}){vault.save(it.getString("token"));password.text.clear();refresh()}}
            area.addView(button(tr("Sign in","লগইন")){submit(false)});area.addView(button(tr("Create account","অ্যাকাউন্ট খুলুন")){submit(true)})
        }else{add(data.optJSONObject("user")?.optString("email")?:tr("Signed in","লগইন করা আছে"));val name=field(tr("Display name","আপনার নাম"));name.setText(data.optJSONObject("user")?.optString("name")?:"");area.addView(button(tr("Save profile","নাম সংরক্ষণ")){async({api.request("/profile","PATCH",JSONObject().put("name",name.text.toString()))}){refresh()}});area.addView(button(tr("Sync devices","সিঙ্ক করুন")){refresh()});area.addView(button(tr("Sign out","লগআউট")){async({api.request("/auth/logout","POST")}){vault.clear();data=JSONObject();draw()}})
            area.addView(button(tr("Delete account & study access","অ্যাকাউন্ট ও পড়ার অনুমতি মুছুন")){AlertDialog.Builder(this).setTitle(tr("Permanently delete account?","অ্যাকাউন্ট স্থায়ীভাবে মুছবেন? ")).setMessage(tr("Credits, access and account history will be deleted.","ক্রেডিট, পড়ার অনুমতি ও অ্যাকাউন্টের ইতিহাস মুছে যাবে।")).setNegativeButton(tr("Cancel","বাতিল"),null).setPositiveButton(tr("Delete","মুছুন")){_,_->async({api.request("/account","DELETE")}){vault.clear();data=JSONObject();draw()}}.show()})}
        area.addView(button(tr("Ad privacy choices","বিজ্ঞাপনের গোপনীয়তা")){ads.privacy {}})
        area.addView(button(tr("Privacy policy","গোপনীয়তার নীতি")){AlertDialog.Builder(this).setTitle(tr("Privacy & protected study","গোপনীয়তা ও সুরক্ষিত পড়া")).setMessage(tr("We store your email, salted password hash, profile, verified ad transactions, credits, access expiry and basic access/security events on the study server. Session tokens are encrypted with Android Keystore. Google AdMob processes advertising/device information under your privacy choices. Credits are granted only after server verification. Screenshots and ordinary screen recording are blocked where Android supports it; external cameras and modified devices cannot be fully blocked. Delete your account in this screen or contact support.","স্টাডি সার্ভারে ইমেইল, পাসওয়ার্ডের সুরক্ষিত হ্যাশ, নাম, যাচাইকৃত বিজ্ঞাপন, ক্রেডিট, পড়ার সময় ও নিরাপত্তার তথ্য থাকে। লগইন টোকেন Android Keystore দিয়ে এনক্রিপ্ট করা হয়। Google AdMob আপনার গোপনীয়তার পছন্দ অনুযায়ী বিজ্ঞাপনের তথ্য প্রক্রিয়া করে। সার্ভার যাচাই করলেই ক্রেডিট পাওয়া যায়। Android সমর্থন করলে স্ক্রিনশট ও সাধারণ রেকর্ডিং বন্ধ থাকে। বাইরের ক্যামেরা বা পরিবর্তিত ডিভাইস পুরোপুরি আটকানো যায় না। এই পৃষ্ঠা থেকে অ্যাকাউন্ট মুছতে পারবেন।")).setPositiveButton("OK",null).show()})
        area.addView(button(tr("Support","সহায়তা")){AlertDialog.Builder(this).setTitle("Hossain Najmul").setMessage("WhatsApp: +81 70-9036-6509\nhttps://devnazu.online/").setPositiveButton("OK",null).show()})
    }
    @Suppress("SetJavaScriptEnabled")
    private fun openReader(route:String,level:String?){
        if(level!=null&&expiry(level)<=now()){tab="Rewards";draw();return}
        readerLevel=level;readerExpiry=level?.let{expiry(it)}?:Long.MAX_VALUE
        val container=LinearLayout(this).apply{orientation=LinearLayout.VERTICAL;setPadding(0,dp(28),0,0);setBackgroundColor(paper)}
        container.addView(button(tr("← Library","← বইঘর")){closeReader()})
        val loader=WebViewAssetLoader.Builder().addPathHandler("/assets/",WebViewAssetLoader.AssetsPathHandler(this)).build()
        val view=WebView(this);web=view
        view.settings.apply{javaScriptEnabled=true;domStorageEnabled=true;allowFileAccess=false;allowContentAccess=false;cacheMode=WebSettings.LOAD_NO_CACHE;setSupportMultipleWindows(false);mixedContentMode=WebSettings.MIXED_CONTENT_NEVER_ALLOW;mediaPlaybackRequiresUserGesture=true}
        WebView.setWebContentsDebuggingEnabled(false)
        view.addJavascriptInterface(object{
            @JavascriptInterface fun speak(text:String){runOnUiThread{tts?.speak(text.take(2000),TextToSpeech.QUEUE_FLUSH,null,"study")}}
            @JavascriptInterface fun stopSpeech(){tts?.stop()}
        },"StudyNative")
        view.webViewClient=object:WebViewClient(){
            override fun shouldOverrideUrlLoading(v:WebView,r:WebResourceRequest):Boolean {
                if(!Access.internal(r.url.toString())){message(tr("This link is outside the study library.","এই লিংকটি স্টাডি লাইব্রেরির বাইরে।"));return true}
                val p=r.url.path?:""
                val next=Regex("/n([1-5])\\.html$").find(p)?.let{"N"+it.groupValues[1]}
                if(next!=null&&next!=readerLevel){closeReader();chooseSubject(next);return true}
                if(p.endsWith("listening.html")){val n=r.url.getQueryParameter("level")?:"N5";if(n!=readerLevel){closeReader();chooseSubject(n);return true}}
                return false
            }
            override fun shouldInterceptRequest(v:WebView,r:WebResourceRequest):WebResourceResponse {
                fun denied(code:Int=403)=WebResourceResponse("text/plain","UTF-8",code,if(code==403)"Forbidden" else "Unavailable",mapOf("Cache-Control" to "no-store"),ByteArrayInputStream("Access unavailable. Return to Reward Center and refresh.".toByteArray()))
                if(!Access.internal(r.url.toString()))return denied()
                val path=r.url.path!!.removePrefix("/assets/reader/")
                val protected=path.startsWith("pdfs/")||path.startsWith("audio/")||Regex("^data/(?:lessons-|owner-|listening-)?n[1-5]\\.json$").matches(path)||path=="data/extra.json"
                if(protected){return try{val (type,bytes)=api.content(path);WebResourceResponse(type.substringBefore(';'),null,200,"OK",mapOf("Cache-Control" to "no-store"),ByteArrayInputStream(bytes))}catch(_:Exception){denied(503)}}
                return loader.shouldInterceptRequest(r.url)?:denied()
            }
            override fun onPageFinished(v:WebView,url:String){v.evaluateJavascript("localStorage.setItem('nihongo-path',JSON.stringify({...JSON.parse(localStorage.getItem('nihongo-path')||'{}'),lang:'${if(bn)"bn" else "en"}'}));if(typeof state!=='undefined'){state.lang='${if(bn)"bn" else "en"}';persist();render();}",null)}
        }
        container.addView(view,LinearLayout.LayoutParams(-1,0,1f));setContentView(container);view.loadUrl("https://appassets.androidplatform.net/assets/reader/$route")
    }
    private fun closeReader(){web?.apply{stopLoading();loadUrl("about:blank");removeJavascriptInterface("StudyNative");clearCache(true);destroy()};web=null;readerLevel=null;tts?.stop();draw()}
    override fun onPause(){web?.onPause();tts?.stop();super.onPause()}
    override fun onResume(){super.onResume();web?.onResume();if(web!=null&&readerLevel!=null)refresh{if(expiry(readerLevel!!)<=now())closeReader()}}
    override fun onDestroy(){handler.removeCallbacksAndMessages(null);web?.destroy();tts?.shutdown();worker.shutdownNow();super.onDestroy()}
}

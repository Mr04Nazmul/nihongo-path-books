package online.devnazu.books

import android.app.Activity
import com.google.android.gms.ads.*
import com.google.android.gms.ads.rewarded.*
import com.google.android.ump.*

class RewardAds(private val activity: Activity) {
    private val consent=UserMessagingPlatform.getConsentInformation(activity)
    private var busy=false
    fun updateConsent(done: () -> Unit) {
        consent.requestConsentInfoUpdate(activity,ConsentRequestParameters.Builder().build(),{
            UserMessagingPlatform.loadAndShowConsentFormIfRequired(activity) { done() }
        },{ done() })
    }
    fun privacy(done: () -> Unit) { UserMessagingPlatform.showPrivacyOptionsForm(activity) { done() } }
    fun show(sessionId: String, userId: String, status: (String) -> Unit, finished: () -> Unit) {
        if(busy)return
        if(!consent.canRequestAds()){status("Ads are unavailable until privacy choices are ready. No credits were deducted.");return}
        busy=true;status("Loading a Google test advertisement…")
        MobileAds.initialize(activity) {
            activity.runOnUiThread {
                RewardedAd.load(activity,BuildConfig.REWARDED_ID,AdRequest.Builder().build(),object:RewardedAdLoadCallback(){
                    override fun onAdFailedToLoad(error:LoadAdError){busy=false;status("No ad is available now. Please try later. Your credits are safe.")}
                    override fun onAdLoaded(ad:RewardedAd){
                        ad.setServerSideVerificationOptions(ServerSideVerificationOptions.Builder().setUserId(userId).setCustomData(sessionId).build())
                        ad.fullScreenContentCallback=object:FullScreenContentCallback(){
                            override fun onAdDismissedFullScreenContent(){busy=false;finished()}
                            override fun onAdFailedToShowFullScreenContent(error:AdError){busy=false;status("Ad could not play. Your credits are safe.")}
                        }
                        ad.show(activity) { status("Ad completed. Waiting for secure server verification…") }
                        // The device callback NEVER changes credits. Only verified SSV can grant them.
                    }
                })
            }
        }
    }
}

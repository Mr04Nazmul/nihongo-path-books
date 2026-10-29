package online.devnazu.books
import android.view.WindowManager
import androidx.test.core.app.ActivityScenario
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Test
import org.junit.Assert.*
import org.junit.runner.RunWith
@RunWith(AndroidJUnit4::class)
class ProtectionTest {
 @Test fun secureWindowAndLaunch(){ActivityScenario.launch(MainActivity::class.java).use{scenario->scenario.onActivity{activity->assertTrue(activity.window.attributes.flags and WindowManager.LayoutParams.FLAG_SECURE != 0);assertNotNull(activity.findViewById<android.view.View>(android.R.id.content))}}}
 @Test fun accountHasGoogleAndMaskedPassword(){
  ActivityScenario.launch(MainActivity::class.java).use{scenario->scenario.onActivity{a->
   fun views(v:android.view.View):List<android.view.View> = listOf(v)+(if(v is android.view.ViewGroup)(0 until v.childCount).flatMap{views(v.getChildAt(it))}else emptyList())
   fun buttons()=views(a.findViewById(android.R.id.content)).filterIsInstance<android.widget.Button>()
   buttons().first{it.text.toString() in listOf("Account","অ্যাকাউন্ট")}.performClick()
   val all=views(a.findViewById(android.R.id.content));val labels=all.filterIsInstance<android.widget.TextView>().map{it.text.toString()}
   assertTrue(labels.any{it.contains("Google")});assertFalse(labels.any{it in listOf("Support","সহায়তা","Privacy policy","গোপনীয়তার নীতি")})
   val password=all.filterIsInstance<android.widget.EditText>().first{it.inputType and android.text.InputType.TYPE_MASK_VARIATION==android.text.InputType.TYPE_TEXT_VARIATION_PASSWORD};assertTrue(password.transformationMethod is android.text.method.PasswordTransformationMethod)
  };androidx.test.platform.app.InstrumentationRegistry.getInstrumentation().waitForIdleSync();scenario.onActivity{a->
   val decor=a.window.decorView;val bitmap=android.graphics.Bitmap.createBitmap(decor.width,decor.height,android.graphics.Bitmap.Config.ARGB_8888);decor.draw(android.graphics.Canvas(bitmap));java.io.File(a.filesDir,"auth-preview.png").outputStream().use{bitmap.compress(android.graphics.Bitmap.CompressFormat.PNG,100,it)};bitmap.recycle()
   fun descendants(v:android.view.View):List<android.view.View> = listOf(v)+(if(v is android.view.ViewGroup)(0 until v.childCount).flatMap{descendants(v.getChildAt(it))}else emptyList())
   descendants(decor).filterIsInstance<android.widget.Button>().first{it.text.toString() in listOf("New here? Create an account","নতুন? অ্যাকাউন্ট খুলুন")}.performClick()
  };androidx.test.platform.app.InstrumentationRegistry.getInstrumentation().waitForIdleSync();scenario.onActivity{a->
   val decor=a.window.decorView
   assertEquals(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE,a.window.attributes.softInputMode and WindowManager.LayoutParams.SOFT_INPUT_MASK_ADJUST)
   val bitmap=android.graphics.Bitmap.createBitmap(decor.width,decor.height,android.graphics.Bitmap.Config.ARGB_8888);decor.draw(android.graphics.Canvas(bitmap));java.io.File(a.filesDir,"signup-preview.png").outputStream().use{bitmap.compress(android.graphics.Bitmap.CompressFormat.PNG,100,it)};bitmap.recycle()
  }}
 }
 @Test fun secureContentNotVisibleInScreenCapture(){
  ActivityScenario.launch(MainActivity::class.java).use { scenario ->
   scenario.onActivity { a -> assertTrue(a.window.attributes.flags and WindowManager.LayoutParams.FLAG_SECURE != 0) }
   val automation=androidx.test.platform.app.InstrumentationRegistry.getInstrumentation().uiAutomation
   automation.waitForIdle(1000,10000)
   val shot=automation.takeScreenshot() ?: return
   try {
    val points=listOf(0.3f,0.4f,0.5f,0.6f,0.7f)
    for(x in points)for(y in points){val pixel=shot.getPixel((shot.width*x).toInt(),(shot.height*y).toInt());assertTrue("Protected app pixels visible in capture",android.graphics.Color.red(pixel)<8&&android.graphics.Color.green(pixel)<8&&android.graphics.Color.blue(pixel)<8)}
   }finally{shot.recycle()}
  }
 }
}

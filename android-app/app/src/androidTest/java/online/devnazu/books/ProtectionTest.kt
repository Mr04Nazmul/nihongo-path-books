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

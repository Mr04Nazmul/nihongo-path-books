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
}

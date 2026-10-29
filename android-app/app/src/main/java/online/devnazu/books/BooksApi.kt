package online.devnazu.books

import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.util.concurrent.TimeUnit

class ApiError(val code: Int, message: String): IllegalStateException(message)

class BooksApi(private val token: () -> String) {
    private val client=OkHttpClient.Builder().connectTimeout(15,TimeUnit.SECONDS).readTimeout(45,TimeUnit.SECONDS).followRedirects(false).build()
    val configured get()=BuildConfig.API_BASE.startsWith("https://")
    fun request(path: String, method: String="GET", data: JSONObject?=null): JSONObject {
        check(configured) { "Study server setup is pending. Free basics are available offline." }
        val b=Request.Builder().url(BuildConfig.API_BASE.trimEnd('/')+path).header("Authorization","Bearer "+token())
        if(method!="GET")b.method(method,(data?:JSONObject()).toString().toRequestBody("application/json".toMediaType()))
        client.newCall(b.build()).execute().use { r ->
            val json=JSONObject(r.body?.string()?:"{}")
            if(!r.isSuccessful)throw ApiError(r.code,json.optString("error","Please try again later"))
            return json
        }
    }
    fun content(path: String): Pair<String,ByteArray> {
        check(configured) { "Server setup pending" }
        val encoded=path.split('/').joinToString("/") { java.net.URLEncoder.encode(it,"UTF-8").replace("+","%20") }
        val req=Request.Builder().url(BuildConfig.API_BASE.trimEnd('/')+"/content/"+encoded).header("Authorization","Bearer "+token()).header("Cache-Control","no-store").build()
        client.newCall(req).execute().use { r ->
            check(r.isSuccessful) { "Access unavailable" }
            return (r.header("Content-Type")?:"application/octet-stream") to (r.body?.bytes()?:byteArrayOf())
        }
    }
}

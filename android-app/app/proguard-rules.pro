# ProGuard rules for Iraqi AI Smart Speaker
-keep class com.iraqi.smart.speaker.data.model.** { *; }
-keepclassmembers class * {
    @com.google.gson.annotations.SerializedName <fields>;
}

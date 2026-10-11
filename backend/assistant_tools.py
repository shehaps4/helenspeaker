"""
Assistant Function Calling & Tools Dispatcher
Provides structured tools schemas for Gemini Live Function Calling.
Includes security validation and parameter boundary checks.
"""

from typing import Dict, Any, Callable

class AssistantToolRegistry:
    
    TOOLS_SCHEMA = [
        {
            "name": "play_music",
            "description": "تشغيل مقطع موسيقي أو أغنية من مكتبة الأغاني المتاحة أو تغيير حالة التشغيل",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "action": {
                        "type": "STRING",
                        "enum": ["play", "pause", "resume", "next", "previous", "stop"],
                        "description": "الإجراء المطلوب لتشغيل الموسيقى"
                    },
                    "track_name": {
                        "type": "STRING",
                        "description": "اسم الأغنية أو الفنان المطلوب (مثلاً: حلو حبك، هيثم يوسف)"
                    }
                },
                "required": ["action"]
            }
        },
        {
            "name": "tell_story",
            "description": "سرد حكاية أو قصة تراثية عراقية أو قصة للأطفال مع دعم تقسيم الفصول",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "story_category": {
                        "type": "STRING",
                        "enum": ["iraqi_folklore", "bedtime_story", "historical", "comedy"],
                        "description": "تصنيف القصة"
                    },
                    "action": {
                        "type": "STRING",
                        "enum": ["start", "continue", "stop"],
                        "description": "بدء قصة جديدة أو إكمال الفصل التالي"
                    }
                },
                "required": ["action"]
            }
        },
        {
            "name": "set_rgb_led",
            "description": "التحكم في إضاءة الـ RGB المدمجة بالسماعة واختيار اللون ونمط الحركة",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "color_hex": {
                        "type": "STRING",
                        "description": "كود اللون بصيغة Hex (مثلاً: #00DCFF للسماوي أو #FF0000 للأحمر)"
                    },
                    "mode": {
                        "type": "STRING",
                        "enum": ["solid", "pulse", "rainbow", "music_sync", "off"],
                        "description": "نمط الإضاءة"
                    },
                    "brightness": {
                        "type": "INTEGER",
                        "description": "شدة السطوع من 0 إلى 255"
                    }
                },
                "required": ["mode"]
            }
        },
        {
            "name": "switch_bluetooth_mode",
            "description": "التبديل بين وضع المساعد الصوتي الذكي AI ووضع سماعة البلوتوث التقليدية A2DP",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "speaker_mode_enabled": {
                        "type": "BOOLEAN",
                        "description": "True لتفعيل وضع سماعة البلوتوث العادية، False للعودة لوضع المساعد الذكي"
                    }
                },
                "required": ["speaker_mode_enabled"]
            }
        },
        {
            "name": "adjust_volume",
            "description": "رفع أو خفض أو ضبط مستوى الصوت العتادي للسماعة",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "level": {
                        "type": "INTEGER",
                        "description": "مستوى الصوت بالنسبة المئوية من 0 إلى 100"
                    }
                },
                "required": ["level"]
            }
        }
    ]

    def __init__(self, hardware_adapter=None):
        self.hardware_adapter = hardware_adapter
        self.handlers: Dict[str, Callable] = {}
        self._register_default_handlers()

    def _register_default_handlers(self):
        self.handlers["play_music"] = self._handle_music
        self.handlers["tell_story"] = self._handle_story
        self.handlers["set_rgb_led"] = self._handle_rgb
        self.handlers["switch_bluetooth_mode"] = self._handle_bluetooth_mode
        self.handlers["adjust_volume"] = self._handle_volume

    def execute_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Validate security boundaries and execute the tool safely."""
        if name not in self.handlers:
            return {"status": "error", "message": f"الأداة غير معروفة: {name}"}
        try:
            handler = self.handlers[name]
            result = handler(args)
            return {"status": "success", "data": result}
        except Exception as e:
            return {"status": "error", "message": f"فشل تنفيذ الأداة: {str(e)}"}

    def _handle_music(self, args: Dict[str, Any]) -> str:
        action = args.get("action")
        track = args.get("track_name", "الأغنية الحالية")
        if self.hardware_adapter:
            self.hardware_adapter.control_music(action, track)
        return f"تم تنفيذ إجراء الموسيقى: {action} للمسار: {track}"

    def _handle_story(self, args: Dict[str, Any]) -> str:
        action = args.get("action")
        cat = args.get("story_category", "iraqi_folklore")
        return f"جاهز للقصة: {cat}، الحالة: {action}"

    def _handle_rgb(self, args: Dict[str, Any]) -> str:
        mode = args.get("mode")
        color = args.get("color_hex", "#00DCFF")
        brightness = max(0, min(255, args.get("brightness", 200)))
        if self.hardware_adapter:
            self.hardware_adapter.set_rgb(color, mode, brightness)
        return f"تم تغيير الإضاءة للنمط: {mode} واللون: {color}"

    def _handle_bluetooth_mode(self, args: Dict[str, Any]) -> str:
        enabled = args.get("speaker_mode_enabled", False)
        if self.hardware_adapter:
            self.hardware_adapter.set_bluetooth_speaker_mode(enabled)
        mode_str = "سماعة بلوتوث عادية" if enabled else "المساعد الذكي"
        return f"تم التبديل بنجاح إلى: {mode_str}"

    def _handle_volume(self, args: Dict[str, Any]) -> str:
        level = max(0, min(100, args.get("level", 80)))
        if self.hardware_adapter:
            self.hardware_adapter.set_volume(level)
        return f"تم ضبط مستوى الصوت على: {level}%"

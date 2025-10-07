# src/core/template_manager.py
import json
import os
import datetime

class TemplateManager:
    """
    水印模板管理器，负责模板的保存、加载和删除
    """
    
    def __init__(self):
        # 获取用户目录
        self.user_dir = os.path.expanduser("~")
        # 创建程序配置目录
        self.config_dir = os.path.join(self.user_dir, ".photo_watermark_tool")
        # 模板保存目录
        self.templates_dir = os.path.join(self.config_dir, "templates")
        # 上次设置文件
        self.last_settings_file = os.path.join(self.config_dir, "last_settings.json")
        # 默认模板文件
        self.default_template_file = os.path.join(self.config_dir, "default_template.json")
        
        # 确保目录存在
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)
    
    def save_template(self, template_name, settings):
        """
        保存水印设置为模板
        
        Args:
            template_name: 模板名称
            settings: 水印设置字典
        
        Returns:
            bool: 是否保存成功
        """
        try:
            # 添加元数据
            template_data = {
                'name': template_name,
                'created_at': datetime.datetime.now().isoformat(),
                'settings': settings
            }
            
            # 保存到文件
            template_file = os.path.join(self.templates_dir, f"{template_name}.json")
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"保存模板失败: {e}")
            return False
    
    def load_template(self, template_name):
        """
        加载水印模板
        
        Args:
            template_name: 模板名称
        
        Returns:
            dict: 水印设置字典，如果加载失败返回None
        """
        try:
            template_file = os.path.join(self.templates_dir, f"{template_name}.json")
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            return template_data['settings']
        except Exception as e:
            print(f"加载模板失败: {e}")
            return None
    
    def delete_template(self, template_name):
        """
        删除水印模板
        
        Args:
            template_name: 模板名称
        
        Returns:
            bool: 是否删除成功
        """
        try:
            template_file = os.path.join(self.templates_dir, f"{template_name}.json")
            if os.path.exists(template_file):
                os.remove(template_file)
                return True
            return False
        except Exception as e:
            print(f"删除模板失败: {e}")
            return False
    
    def get_all_templates(self):
        """
        获取所有已保存的模板
        
        Returns:
            list: 模板名称列表
        """
        try:
            templates = []
            if os.path.exists(self.templates_dir):
                for filename in os.listdir(self.templates_dir):
                    if filename.endswith('.json'):
                        # 移除.json扩展名
                        template_name = filename[:-5]
                        templates.append(template_name)
            return sorted(templates)
        except Exception as e:
            print(f"获取模板列表失败: {e}")
            return []
    
    def save_last_settings(self, settings):
        """
        保存最后一次使用的设置
        
        Args:
            settings: 水印设置字典
        """
        try:
            with open(self.last_settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存最后设置失败: {e}")
    
    def load_last_settings(self):
        """
        加载最后一次使用的设置
        
        Returns:
            dict: 水印设置字典，如果不存在则返回None
        """
        try:
            if os.path.exists(self.last_settings_file):
                with open(self.last_settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"加载最后设置失败: {e}")
            return None
    
    def save_default_template(self, settings):
        """
        保存默认模板
        
        Args:
            settings: 水印设置字典
        """
        try:
            with open(self.default_template_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存默认模板失败: {e}")
    
    def load_default_template(self):
        """
        加载默认模板
        
        Returns:
            dict: 水印设置字典，如果不存在则返回None
        """
        try:
            if os.path.exists(self.default_template_file):
                with open(self.default_template_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"加载默认模板失败: {e}")
            return None
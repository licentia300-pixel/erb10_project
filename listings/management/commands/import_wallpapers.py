import os
import re
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from django.contrib.auth.models import User
from listings.models import Wallpaper
from listings.choices import CATEGORY_CHOICES, FORMAT_CHOICES
from PIL import Image


class Command(BaseCommand):
    help = 'Import wallpapers from folder with subfolders as categories.'

    def add_arguments(self, parser):
        parser.add_argument(
            'folder',
            type=str,
            help='Path to the root folder containing subfolders: city_view, animation, nature, space'
        )

    def clean_title(self, filename):
        """
        从文件名中提取干净的标题，移除分辨率、随机数字等
        """
        # 1. 去掉扩展名
        name = os.path.splitext(filename)[0]

        # 2. 移除分辨率模式 (如 3840x2160, 1920x1080)
        name = re.sub(r'[-_]?\d+x\d+[-_]?', ' ', name, flags=re.IGNORECASE)

        # 3. 移除末尾的随机数字 (如 -9621, _5678)
        name = re.sub(r'[-_]?\d+$', '', name).strip()

        # 4. 将 - 和 _ 替换为空格
        name = name.replace('_', ' ').replace('-', ' ')

        # 5. 将多个空格合并为一个
        name = ' '.join(name.split())

        # 6. 首字母大写 (title case)
        return name.title()

    def handle(self, *args, **options):
        root_path = options['folder']
        if not os.path.isdir(root_path):
            self.stderr.write(self.style.ERROR(f'Folder "{root_path}" does not exist.'))
            return

        # 获取超级管理员用户
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stderr.write(self.style.ERROR('No superuser found. Please run: python manage.py createsuperuser'))
            return

        # 分类与文件夹名映射
        valid_categories = [choice[0] for choice in CATEGORY_CHOICES]

        # 格式映射
        format_map = {
            'JPEG': 'jpeg',
            'JPG': 'jpeg',
            'PNG': 'png',
            'WEBP': 'webp',
        }

        self.stdout.write(self.style.SUCCESS(f'Scanning folder: {root_path}'))

        imported_count = 0
        skipped_count = 0

        # 遍历根目录下的子文件夹
        for folder_name in os.listdir(root_path):
            folder_path = os.path.join(root_path, folder_name)

            if not os.path.isdir(folder_path):
                continue

            if folder_name not in valid_categories:
                self.stdout.write(self.style.WARNING(f'Skipping unknown folder: {folder_name}'))
                skipped_count += 1
                continue

            category = folder_name
            self.stdout.write(f'Processing category: {category}')

            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)

                if not os.path.isfile(file_path):
                    continue

                ext = filename.split('.')[-1].lower()
                if ext not in ['jpg', 'jpeg', 'png', 'webp']:
                    continue

                try:
                    # 1. 读取图片元数据
                    with Image.open(file_path) as img:
                        width, height = img.size
                        resolution = f"{width}x{height}"
                        img_format = img.format.upper() if img.format else 'JPEG'

                    # 2. 文件大小
                    size_bytes = os.path.getsize(file_path)
                    size_mb = size_bytes / (1024 * 1024)
                    filesize = f"{size_mb:.1f} MB" if size_mb >= 1 else f"{size_mb * 1024:.0f} KB"

                    # 3. 清理标题（自动去除分辨率、随机数字）
                    title = self.clean_title(filename)

                    # 4. 格式映射
                    format_key = format_map.get(img_format, 'jpeg')

                    # 5. 检查是否已存在（按标题 + 分类去重）
                    if Wallpaper.objects.filter(title=title, category=category).exists():
                        self.stdout.write(self.style.WARNING(f'  Skipped: {title} (already exists)'))
                        continue

                    # 6. 创建 Wallpaper 对象
                    wallpaper = Wallpaper(
                        title=title,
                        category=category,
                        resolution=resolution,
                        format=format_key,
                        filesize=filesize,
                        uploaded_by=admin_user,
                    )

                    # 7. 保存图片到 image 字段
                    with open(file_path, 'rb') as f:
                        wallpaper.image.save(filename, File(f), save=False)

                    wallpaper.save()

                    self.stdout.write(self.style.SUCCESS(f'  Imported: {title} ({resolution}, {filesize})'))
                    imported_count += 1

                except Exception as e:
                    self.stderr.write(self.style.ERROR(f'  Error importing {filename}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'\nDone! Imported: {imported_count}, Skipped: {skipped_count}'))
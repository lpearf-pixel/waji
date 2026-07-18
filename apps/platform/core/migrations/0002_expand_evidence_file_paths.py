import core.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_gate0_field_capture"),
    ]

    operations = [
        migrations.AlterField(
            model_name="capture",
            name="raw_file",
            field=models.FileField(max_length=500, upload_to=core.models.capture_audio_path),
        ),
        migrations.AlterField(
            model_name="capture",
            name="position_photo",
            field=models.FileField(blank=True, max_length=500, null=True, upload_to=core.models.position_photo_path),
        ),
        migrations.AlterField(
            model_name="capture",
            name="processed_file",
            field=models.FileField(blank=True, max_length=500, null=True, upload_to=core.models.processed_audio_path),
        ),
    ]

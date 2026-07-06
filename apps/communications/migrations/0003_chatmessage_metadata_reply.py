# Generated for chat attachment metadata and one-level replies.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("communications", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="chatmessage",
            name="content_type",
            field=models.CharField(blank=True, max_length=127),
        ),
        migrations.AddField(
            model_name="chatmessage",
            name="parent",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="replies",
                to="communications.chatmessage",
            ),
        ),
        migrations.AddField(
            model_name="chatmessage",
            name="size_bytes",
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="chatmessage",
            name="kind",
            field=models.CharField(
                choices=[
                    ("text", "Text"),
                    ("image", "Image"),
                    ("file", "File"),
                    ("video", "Video"),
                    ("voice", "Voice"),
                ],
                default="text",
                max_length=16,
            ),
        ),
        migrations.AlterField(
            model_name="chatmessage",
            name="name",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]

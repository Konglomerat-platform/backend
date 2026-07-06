import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("communications", "0003_chatmessage_metadata_reply"),
    ]

    operations = [
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
                    ("album", "Album"),
                ],
                default="text",
                max_length=16,
            ),
        ),
        migrations.CreateModel(
            name="ChatAttachment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "kind",
                    models.CharField(
                        choices=[("image", "Image"), ("file", "File"), ("video", "Video")],
                        default="file",
                        max_length=16,
                    ),
                ),
                ("file", models.FileField(upload_to="chat/attachments/")),
                ("name", models.CharField(blank=True, max_length=255)),
                ("content_type", models.CharField(blank=True, max_length=127)),
                ("size_bytes", models.PositiveBigIntegerField(blank=True, null=True)),
                ("sort_order", models.PositiveSmallIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "message",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attachments",
                        to="communications.chatmessage",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order", "id"],
            },
        ),
    ]

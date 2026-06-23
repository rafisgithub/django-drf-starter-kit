from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_user_is_otp_verified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='term_and_condition_accepted',
            field=models.BooleanField(default=False),
        ),
    ]

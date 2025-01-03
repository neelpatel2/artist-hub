# Generated by Django 5.1 on 2024-09-18 02:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('artist', '0002_artistprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArtistCatalogueCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='artist',
            name='otp',
            field=models.CharField(default='545663', max_length=255),
        ),
        migrations.AlterField(
            model_name='artistprofile',
            name='address',
            field=models.CharField(blank=True, default='-', max_length=255, null=True),
        ),
        migrations.CreateModel(
            name='ArtistCatalogue',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('artist_catalogue_id', models.CharField(blank=True, max_length=255, primary_key=True, serialize=False)),
                ('catalogue_image', models.ImageField(default='default-images/default-catalogue-image.png', upload_to='')),
                ('title', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('artist_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='artist.artist')),
                ('categories', models.ManyToManyField(related_name='catalogues', to='artist.artistcataloguecategory')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

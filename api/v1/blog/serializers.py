from django.conf import settings
from django.utils import translation
from rest_framework import serializers

from blog.models import News, TinyMCEPicture, Currency, Category, Tags, Account
from rest_framework import serializers


class StdImageField(serializers.ImageField):
    """
    Get all the variations of the StdImageField
    """

    def to_native(self, obj):
        return self.get_variations_urls(obj)

    def to_representation(self, obj):
        return self.get_variations_urls(obj)

    def get_variations_urls(self, obj):
        """
        Get all the logo urls.
        """

        # Initiate return object
        return_object = {}

        # Get the field of the object
        field = obj.field

        # A lot of ifs going around, first check if it has the field variations
        if hasattr(field, 'variations'):
            # Get the variations
            variations = field.variations
            # Go through the variations dict
            for key in variations.keys():
                # Just to be sure if the stdimage object has it stored in the obj
                if hasattr(obj, key):
                    # get the by stdimage properties
                    field_obj = getattr(obj, key, None)
                    if field_obj and hasattr(field_obj, 'url'):
                        # store it, with the name of the variation type into our return object
                        return_object[key] = super(StdImageField, self).to_representation(field_obj)

        # Also include the original (if possible)
        if hasattr(obj, 'url'):
            return_object['original'] = super(StdImageField, self).to_representation(obj)

        return return_object


class I18nModelSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        i18n_fields = getattr(self.Meta, 'i18n_fields', None)
        fields_lang = [f"{field}_{key}" for field in i18n_fields[1] for key, _ in settings.LANGUAGES]
        representation = super().to_representation(instance)
        if i18n_fields[0] == 'catch':
            for k in i18n_fields[1]:
                representation[f'{k}'] = representation.pop("{}_{}".format(k, translation.get_language()))
                if not getattr(instance, "{}_{}".format(k, translation.get_language()), None):
                    for iso, _ in settings.LANGUAGES:
                        if getattr(instance, f'{k}_{iso}', None):
                            representation[f'{k}'] = representation.pop("{}_{}".format(k, iso))
                            break
                        else:
                            continue
                if not representation[k]:
                    representation[k] = None
        return {key: value for key, value in representation.items() if key not in fields_lang}


class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = "__all__"


class CategorySerializer(I18nModelSerializer):
    class Meta:
        model = Category
        i18n_fields = ("catch", ('name',))
        fields = "__all__"


class NewsSerializer(I18nModelSerializer):
    picture = StdImageField()
    category = CategorySerializer()
    tags = TagsSerializer(many=True)
    url = serializers.SerializerMethodField(source='slug')

    class Meta:
        model = News
        i18n_fields = ("catch", ('title', 'description', 'brief'))
        # fields = '__all__'
        exclude = 'slug', 'tg_image_uz', 'tg_image_uz-to', 'created_at', 'updated_at', 'draft', \
            'status', 'view_count', 'created_by', 'updated_by',
        extra_kwargs = {
            "createdBy": {
                'read_only': True,
            },
            "updatedBy": {
                'read_only': True,
            },
            "view_count": {
                'read_only': True,
            }
        }

    def get_url(self, obj):
        return obj.slug


#
# class NewsTagsSerializer(serializers.ModelSerializer):
#     news = NewsSerializer(many=True, required=False, read_only=True)
#     tags = TagsSerializer(many=True, required=False, read_only=True)
#
#     class Meta:
#         model = NewsTags
#         fields = "__all__"
#

class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = "__all__"


class TinyMCEPictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = TinyMCEPicture
        fields = "__all__"


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = "__all__"

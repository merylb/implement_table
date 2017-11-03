from rest_framework import serializers
from rest_framework.fields import CharField, DictField
from rest_framework_mongoengine.serializers import DocumentSerializer, EmbeddedDocumentSerializer

from implement_table.authentication.models import Resource, Profile, MnUser
from implement_table.core.fields import BReferenceField


class ResourceSerializer(EmbeddedDocumentSerializer):
    is_all = serializers.BooleanField()
    actions = DictField(child=CharField(), read_only=False, required=False)

    class Meta:
        model = Resource
        fields = ("name", "is_all", "actions")


class ProfileSerializer(DocumentSerializer):
    default_state = CharField(required=False)
    permissions = DictField(child=ResourceSerializer(), read_only=False, required=False)

    class Meta:
        model = Profile
        fields = ('id', 'is_root', 'name', 'permissions', 'default_state')


class MnUserSerializer(DocumentSerializer):
    password = CharField(write_only=True)
    new_password = CharField(write_only=True, required=False)
    profile = BReferenceField(serializer=ProfileSerializer, read_only=False)

    class Meta:
        model = MnUser
        fields = ('id', 'username', 'password', 'new_password', 'is_active', 'profile')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = MnUser(**validated_data)

        return user.set_password(password)

    def update(self, instance, validated_data):
        old_password = validated_data.pop('password')
        new_password = validated_data.pop('new_password')

        assert instance.check_password(old_password), "old password invalid"

        instance = super(MnUserSerializer, self).update(instance, validated_data)

        return instance.set_password(new_password)

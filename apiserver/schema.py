import graphene
from graphene import ObjectType
from graphene_django import DjangoObjectType

from apiserver.models import Announcement, ServerStatus, Ranking, MyUser


class AnnouncementType(DjangoObjectType):
    class Meta:
        model = Announcement


class ServerstatusType(ObjectType):
    # class Meta:
    #     model = ServerStatus

    version = graphene.Float()
    maintenance = graphene.Boolean()
    forceupdate = graphene.Boolean()

    def resolve_version(self, info, **kwargs):
        return float(ServerStatus.objects.get(description="version").data)

    def resolve_maintenance(self, info, **kwargs):
        return bool(ServerStatus.objects.get(description="isMaintenance").data)

    def resolve_forceupdate(self, info, **kwargs):
        return bool(ServerStatus.objects.get(description="isForceUpdate").data)


class RankingType(DjangoObjectType):
    class Meta:
        model = Ranking


class UserType(DjangoObjectType):
    class Meta:
        model = MyUser
        exclude = ('password', 'id', 'is_superuser', 'email', 'is_staff', 'google_id')


class Query(ObjectType):
    announcements = graphene.List(AnnouncementType)
    announcement = graphene.Field(AnnouncementType, id=graphene.Int())
    serverstati = graphene.List(ServerstatusType)
    serverstatus = graphene.Field(ServerstatusType, field_description=graphene.String())

    rankings = graphene.List(RankingType)
    user = graphene.Field(UserType, username=graphene.String(), google_id=graphene.String())
    userOfID = graphene.Field(UserType, id=graphene.Int())

    # return announcements with title, content, by accept-language in http request
    def resolve_announcements(self, info, **kwargs):
        lang = info.context.META.get('HTTP_ACCEPT_LANGUAGE', '')
        content_column = 'content_' + lang
        title_column = 'title_' + lang
        announcements = Announcement.objects.all()
        for announcement in announcements:
            content = None
            title = None
            try:
                content = getattr(announcement, content_column)
            except:
                pass
            try:
                title = getattr(announcement, title_column)
            except:
                pass
            if content is not None:
                announcement.content = content
            if title is not None:
                announcement.title = title
        return announcements

    # return an announcement by id with title, content, by accept-language in http request
    def resolve_announcement(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            announcement = Announcement.objects.get(pk=id)
            lang = info.context.META.get('HTTP_ACCEPT_LANGUAGE', '')
            content_column = 'content_' + lang
            title_column = 'title_' + lang
            content = None
            title = None
            try:
                content = getattr(announcement, content_column)
            except:
                pass
            try:
                title = getattr(announcement, title_column)
            except:
                pass
            if content is not None:
                announcement.content = content
            if title is not None:
                announcement.title = title
            return announcement
        return None

    def resolve_serverstati(self, info, **kwargs):
        return ServerStatus.objects.all()

    def resolve_serverstatus(self, info, **kwargs):
        return ServerStatus()  # ServerStatus.objects.get(description=kwargs.get('field_description'))

    def resolve_rankings(self, info, **kwargs):
        rankings = Ranking.objects.all()
        for ranking in rankings:
            ranking.user.jewel = 0
            ranking.user.jewel_2 = 0
            ranking.user.experience = 0
            ranking.user.money = 0
        return rankings

    def resolve_user(self, info, **kwargs):
        username = kwargs.get('username')
        google_id = kwargs.get('google_id')
        if username is not None and google_id is not None:
            user = MyUser.objects.get(username=username, google_id=google_id)
            return user

        return None

    def resolve_userOfID(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            theUser = MyUser.objects.get(pk=id)
            # theUser.ranking_set = None
            theUser.jewel = 0
            theUser.money = 0
            theUser.experience = 0
            theUser.jewel_2 = 0
            return theUser
        return None


class UserInput(graphene.InputObjectType):
    # id = graphene.ID()
    name = graphene.String(required=True)
    password = graphene.String()
    google_id = graphene.String()


class LiveResultInput(graphene.InputObjectType):
    # id = graphene.ID()
    userId = graphene.Int()
    time = graphene.DateTime()
    score = graphene.Int(required=True)


class CreateNewUser(graphene.Mutation):
    class Arguments:
        input = UserInput(required=True)

    user = graphene.Field(UserType)

    @staticmethod
    def mutate(root, info, input=None):
        myuser_instance = MyUser(username=input.name, password=input.password, google_id=input.google_id, money=0,
                                 jewel=0, jewel_2=0, experience=0, level=0)
        myuser_instance.save()
        return CreateNewUser()


class NewLiveResult(graphene.Mutation):
    class Arguments:
        input = LiveResultInput(required=True)

    newliveresult = graphene.Field(RankingType)

    @staticmethod
    def mutate(root, info, input=None):
        ranking_instance = Ranking(score=input.score, user_id=input.userId)
        ranking_instance.save()
        return NewLiveResult()


class Mutation(graphene.ObjectType):
    createNewUser = CreateNewUser.Field()
    newLiveResult = NewLiveResult.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)

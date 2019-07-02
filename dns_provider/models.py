from mongoengine import Document, StringField


class DNS(Document):
    ip = StringField(max_length=15, required=True)
    name = StringField(max_length=200, required=True)
    domain = StringField(max_length=150, required=True)

    @property
    def uuid(self):
        return str(self.pk)

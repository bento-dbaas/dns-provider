from dns_provider.database.models import DNS


##DNS
def create_dns(data):
    dns_document = DNS(
        ip=data.get('ip'),
        name=data.get('name'),
        domain=data.get('domain')
    )
    dns_document.save()
    return dns_document


def delete_dns(name, domain):
    dns = DNS.objects(name=name, domain=domain).first()
    dns.delete()

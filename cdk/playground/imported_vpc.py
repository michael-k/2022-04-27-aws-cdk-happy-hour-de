import jsii
from aws_cdk import Fn, Resource, aws_ec2 as ec2
from constructs import Construct, DependencyGroup


@jsii.implements(ec2.IVpc)
class ImportedVPC(Resource, metaclass=jsii.JSIIMeta):
    def __init__(self, scope: Construct, id_: str, *, vpc_id_export_name: str):
        super().__init__(scope, id_)
        self._vpc_id = Fn.import_value(vpc_id_export_name)

    @property  # type: ignore[misc]
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> str:
        return self._vpc_id

    @jsii.member(jsii_name="selectSubnets")
    def select_subnets(self, selection: ec2.SubnetSelection) -> ec2.SelectedSubnets:
        return ec2.SelectedSubnets(
            availability_zones=[],
            has_public=False,
            internet_connectivity_established=DependencyGroup(),
            subnet_ids=[subnet.subnet_id for subnet in selection.subnets],
            subnets=[],
            is_pending_lookup=False,
        )


@jsii.implements(ec2.ISubnet)
class ImportedSubnet(Resource, metaclass=jsii.JSIIMeta):
    def __init__(self, scope: Construct, id_: str, *, subnet_export_name: str):
        super().__init__(scope, id_)
        self._subnet = Fn.import_value(subnet_export_name)

    @property  # type: ignore[misc]
    @jsii.member(jsii_name="subnetId")
    def subnet_id(self) -> str:
        return self._subnet

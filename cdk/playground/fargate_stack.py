from aws_cdk import Fn, Stack, aws_ec2 as ec2
from constructs import Construct


class FargateStack(Stack):
    def __init__(self, scope: Construct, id_: str, **kwargs) -> None:
        super().__init__(scope, id_, **kwargs)

        vpc = ec2.Vpc.from_vpc_attributes(
            self,
            "VPC",
            vpc_id=Fn.import_value("PlaygroundVPCId"),
            availability_zones=["a", "b", "c"],
        )

        ec2.SecurityGroup(self, "SecurityGroup", allow_all_outbound=True, vpc=vpc)

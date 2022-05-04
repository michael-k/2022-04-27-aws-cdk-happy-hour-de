from aws_cdk import Stack, aws_ec2 as ec2, aws_ecs as ecs
from constructs import Construct

from .imported_role import ImportedRole
from .imported_vpc import ImportedSubnet, ImportedVPC


class FargateStack(Stack):
    def __init__(self, scope: Construct, id_: str, **kwargs) -> None:
        super().__init__(scope, id_, **kwargs)

        vpc = ImportedVPC(self, "VPC", vpc_id_export_name="PlaygroundVPCId")

        cluster = ecs.Cluster(self, "FargateCluster", vpc=vpc)
        cluster.enable_fargate_capacity_providers()

        task_definition = ecs.FargateTaskDefinition(
            self,
            "TaskDefinition",
            cpu=1024,
            ephemeral_storage_gib=21,
            memory_limit_mib=4096,
            runtime_platform=ecs.RuntimePlatform(
                cpu_architecture=ecs.CpuArchitecture.X86_64,
                operating_system_family=ecs.OperatingSystemFamily.LINUX,
            ),
            execution_role=ImportedRole(
                self,
                "ExecutionRole",
                arn_export_name="PlaygroundTaskExecutionRoleARN",
                name_export_name="PlaygroundTaskExecutionRoleName",
            ),
            task_role=ImportedRole(
                self,
                "TaskRole",
                arn_export_name="PlaygroundTaskRoleARN",
                name_export_name="",
            ),
        )

        task_definition.add_container(
            "PlaygroundContainer",
            image=ecs.ContainerImage.from_registry("foo"),
            command=["bar"],
            entry_point=["executable"],
            environment={"SOMETHING": "pointless"},
            memory_limit_mib=2048,
        )

        security_group = ec2.SecurityGroup(
            self, "SecurityGroup", allow_all_outbound=True, vpc=vpc
        )

        ecs.FargateService(
            self,
            "FargateService",
            task_definition=task_definition,
            assign_public_ip=False,
            platform_version=ecs.FargatePlatformVersion.VERSION1_4,
            security_groups=[security_group],
            vpc_subnets=ec2.SubnetSelection(
                subnets=[
                    ImportedSubnet(
                        self,
                        f"Subnet{subnet}",
                        subnet_export_name=(f"NlgVpcSubnetPrivate{subnet}"),
                    )
                    for subnet in ("A", "B", "C")
                ]
            ),
            cluster=cluster,
            capacity_provider_strategies=[
                ecs.CapacityProviderStrategy(
                    capacity_provider="FARGATE_SPOT", base=0, weight=1
                )
            ],
            circuit_breaker=ecs.DeploymentCircuitBreaker(rollback=False),
            desired_count=1,
            propagate_tags=ecs.PropagatedTagSource.TASK_DEFINITION,
        )

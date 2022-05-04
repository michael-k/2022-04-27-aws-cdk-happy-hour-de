import jsii
from aws_cdk import Fn, Resource, aws_iam as iam
from constructs import Construct, DependencyGroup


@jsii.implements(iam.IRole)
class ImportedRole(Resource, metaclass=jsii.JSIIMeta):
    def __init__(
        self, scope: Construct, id_: str, *, arn_export_name: str, name_export_name: str
    ):
        super().__init__(scope, id_)
        self._role_arn = Fn.import_value(arn_export_name)
        self._role_name = Fn.import_value(name_export_name)

    @property  # type: ignore
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> str:
        return self._role_arn

    @property  # type: ignore
    @jsii.member(jsii_name="roleName")
    def role_name(self) -> str:
        return self._role_name

    # @jsii.member(jsii_name="attachInlinePolicy")
    # def attach_inline_policy(self, policy: iam.Policy) -> None:
    #     pass

    # @jsii.member(jsii_name="addManagedPolicy")
    # def add_managed_policy(self, policy: iam.IManagedPolicy) -> None:
    #     pass

    # @jsii.member(jsii_name="addToPolicy")
    # def add_to_policy(self, statement: iam.PolicyStatement) -> bool:
    #     return self.add_to_principal_policy(statement).statement_added

    @jsii.member(jsii_name="addToPrincipalPolicy")
    def add_to_principal_policy(
        self, statement: iam.PolicyStatement
    ) -> iam.AddToPrincipalPolicyResult:
        # Pretend that we've added the policy.
        return iam.AddToPrincipalPolicyResult(
            statement_added=True, policy_dependable=DependencyGroup()
        )

    # @jsii.member(jsii_name="grant")
    # def grant(self, grantee: iam.IPrincipal, *actions: str) -> iam.Grant:
    #     return self.role.grant(grantee, *actions)

    # @jsii.member(jsii_name="grantPassRole")
    # def grant_pass_role(self, grantee: iam.IPrincipal) -> iam.Grant:
    #     return self.role.grant_pass_role(grantee)


__all__ = ["ImportedRole"]

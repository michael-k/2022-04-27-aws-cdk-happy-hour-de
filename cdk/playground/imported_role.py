from typing import Optional

import jsii
from aws_cdk import ArnFormat, Fn, Resource, Stack, aws_iam as iam
from constructs import Construct, DependencyGroup


@jsii.implements(iam.IRole)
class ImportedRole(Resource, metaclass=jsii.JSIIMeta):
    def __init__(
        self, scope: Construct, id_: str, *, arn_export_name: str, name_export_name: str
    ):
        super().__init__(scope, id_)
        self._scope = scope
        self._role_arn = Fn.import_value(arn_export_name)
        self._role_name = Fn.import_value(name_export_name)
        self._default_policy: iam.Policy = None

        self.__seen_policies: set[iam.Policy] = set()

    @property  # type: ignore[misc]
    @jsii.member(jsii_name="policyFragment")
    def policy_fragment(self) -> iam.PrincipalPolicyFragment:
        return iam.ArnPrincipal(self.role_arn).policy_fragment

    @property  # type: ignore[misc]
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> str:
        return self._role_arn

    @property  # type: ignore[misc]
    @jsii.member(jsii_name="roleName")
    def role_name(self) -> str:
        return self._role_name

    @property  # type: ignore[misc]
    @jsii.member(jsii_name="grantPrincipal")
    def grant_principal(self) -> iam.IPrincipal:
        return self  # iam.ArnPrincipal(self._role_arn)

    @property  # type: ignore[misc]
    @jsii.member(jsii_name="principalAccount")
    def principal_account(self) -> Optional[str]:
        scope_stack = Stack.of(self._scope)
        parsed_arn = scope_stack.split_arn(
            self._role_arn, ArnFormat.SLASH_RESOURCE_NAME
        )
        return parsed_arn.account

    @jsii.member(jsii_name="attachInlinePolicy")
    def attach_inline_policy(self, policy: iam.Policy) -> None:
        if policy not in self.__seen_policies:
            self.__seen_policies.add(policy)
            policy.attach_to_role(self)

    # @jsii.member(jsii_name="addManagedPolicy")
    # def add_managed_policy(self, policy: iam.IManagedPolicy) -> None:
    #     pass

    @jsii.member(jsii_name="addToPolicy")
    def add_to_policy(self, statement: iam.PolicyStatement) -> bool:
        return self.add_to_principal_policy(statement).statement_added

    @jsii.member(jsii_name="addToPrincipalPolicy")
    def add_to_principal_policy(
        self, statement: iam.PolicyStatement
    ) -> iam.AddToPrincipalPolicyResult:
        if self._default_policy is None:
            self._default_policy = iam.Policy(self, "Policy")
            self.attach_inline_policy(self._default_policy)
        self._default_policy.add_statements(statement)
        return iam.AddToPrincipalPolicyResult(
            statement_added=True, policy_dependable=self._default_policy
        )

    # @jsii.member(jsii_name="grant")
    # def grant(self, grantee: iam.IPrincipal, *actions: str) -> iam.Grant:
    #     return self.role.grant(grantee, *actions)

    # @jsii.member(jsii_name="grantPassRole")
    # def grant_pass_role(self, grantee: iam.IPrincipal) -> iam.Grant:
    #     return self.role.grant_pass_role(grantee)


__all__ = ["ImportedRole"]

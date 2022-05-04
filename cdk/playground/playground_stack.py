from aws_cdk import Fn, Stack, aws_codebuild as codebuild, aws_iam as iam
from constructs import Construct

from .imported_role import ImportedRole


class PlaygroundStack(Stack):
    def __init__(self, scope: Construct, id_: str, **kwargs) -> None:
        super().__init__(scope, id_, **kwargs)

        imported_role = ImportedRole(
            self,
            "CodeBuildRoleImported",
            arn_export_name="CodeBuildRolePlaygroundARN",
            name_export_name="CodeBuildRolePlaygroundName",
        )

        codebuild.Project(
            self,
            "PlaygroundCodeBuild",
            source=codebuild.Source.git_hub(
                owner="owner",
                repo="repo",
                branch_or_ref="main",
                clone_depth=1,
                fetch_submodules=False,
                report_build_status=True,
                webhook=False,
            ),
            build_spec=codebuild.BuildSpec.from_source_filename("buildspec.yml"),
            cache=None,
            description="This is a description.",
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0
                if hasattr(codebuild.LinuxBuildImage, "STANDARD_5_0")
                else codebuild.LinuxBuildImage.STANDARD_4_0,
                compute_type=codebuild.ComputeType.SMALL,
                environment_variables={},
                privileged=True,
            ),
            role=imported_role,
        )

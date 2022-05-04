image_name = aws-cdk-playground
container_name = aws-cdk-playground
container_tag = latest

build-docker:
	docker build --pull --no-cache --tag ${image_name}:${container_tag} -f Dockerfile .

synth:
	mkdir -p ${PWD}/templates
	docker run --rm -it -v ${PWD}:/code -e CDK_DISABLE_VERSION_CHECK=1 --entrypoint cdk ${image_name}:${container_tag} synth playground > templates/playground.yaml

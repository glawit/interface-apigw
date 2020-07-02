set -e

output_directory="$1"

shift

for python_version in "$@"
do
	container_id="$(
		docker \
			run \
			--interactive \
			--tty \
			--detach \
			--volume "${PWD}/glawit:/var/task:ro" \
			-- \
			"lambci/lambda:build-python${python_version}" \
			/bin/sh \
			#
	)"

	for package in core interface_apigw
	do
		docker \
			exec \
			--workdir /var/task \
			-- \
			"${container_id}" \
			pip \
			wheel \
			--no-deps \
			--build /tmp/build \
			--wheel-dir /tmp/whl \
			--progress-bar off \
			-- \
			"./${package}" \
			#
	done

	docker \
		exec \
		-- \
		"${container_id}" \
		sh \
		-c \
		"pip install --target /tmp/deployment_package/python/lib/python${python_version}/site-packages/ /tmp/whl/*" \
		#

	docker \
		cp \
		-- \
		"${container_id}:/tmp/deployment_package/." \
		"${output_directory}" \
		#

	docker \
		container \
		stop \
		-- \
		"${container_id}"

	docker \
		rm \
		-- \
		"${container_id}"
done

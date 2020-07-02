set -e

python_version="$1"
output_directory="$2"

container_id="$(
	docker \
		run \
		--interactive \
		--tty \
		--detach \
		--volume "${PWD}:/var/task:ro" \
		-- \
		"lambci/lambda:build-python${python_version}" \
		/bin/sh \
		#
)"

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
	'./' \
	#

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

import hashlib
import io
import time
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.version import Version

import docker


class CodegenSandboxPool:
    """Manages and reuses sandboxes for efficient resource management."""

    def __init__(self, max_memory="1g", max_cpu=1.0):
        self.client = docker.from_env()
        self.max_memory = max_memory
        self.max_cpu = max_cpu
        self.alloc_memory = 0
        self.alloc_cpu = 0
        self.image_cache = {}
        self.constraints_cache = {}

    def _hash_requirements(self, base_image, packages):
        """Generate a hash for the base image and package list to identify reusable images."""
        requirements_str = f"{base_image}:" + ",".join(sorted(packages or []))
        return hashlib.sha256(requirements_str.encode('utf-8')).hexdigest()

    def _check_compatibility(self, image_id, packages):
        """Check if an image meets the requested package requirements."""
        cached_constraints = self.constraints_cache.get(image_id)
        if not cached_constraints:
            return False

        for req in packages:
            req_parsed = Requirement(req)
            if req_parsed.name not in cached_constraints:
                return False
            if not cached_constraints[req_parsed.name].contains(req_parsed.specifier):
                return False
        return True

    def _create_image(self, base_image, packages):
        """Create a new Docker image with specified packages."""
        dockerfile = f"FROM {base_image}\nRUN pip install {' '.join(packages)}"
        dockerfile_obj = io.BytesIO(dockerfile.encode('utf-8'))
        image, _ = self.client.images.build(fileobj=dockerfile_obj, rm=True)
        image_id = image.id

        # Store package constraints in the cache
        self.constraints_cache[image_id] = {
            req.name: req.specifier for req in map(Requirement, packages)
        }
        return image

    def get_sandbox(self, base_image="python:3.9-slim", packages=None, mem_limit="100m", cpu_quota=0.5):
        """Allocate a sandbox, reusing or creating images as necessary."""
        if float(mem_limit.strip("m")) + self.alloc_memory > float(self.max_memory.strip("g")) * 1024:
            raise SandboxError("Requested memory exceeds pool's maximum allocable memory")
        if cpu_quota + self.alloc_cpu > self.max_cpu:
            raise SandboxError("Requested CPU exceeds pool's maximum allocable CPU")

        requirements_hash = self._hash_requirements(base_image, packages)

        if requirements_hash in self.image_cache:
            image = self.image_cache[requirements_hash]
        else:
            for image_id in self.image_cache.values():
                if self._check_compatibility(image_id, packages):
                    image = image_id
                    break
            else:
                image = self._create_image(base_image, packages)
                self.image_cache[requirements_hash] = image

        sandbox = AICodeSandbox(
            image=image.id,
            mem_limit=mem_limit,
            cpu_quota=int(cpu_quota * 100000)
        )
        self.alloc_memory += float(mem_limit.strip("m"))
        self.alloc_cpu += cpu_quota
        return sandbox

    def release_sandbox(self, sandbox):
        """Release resources from the sandbox and update resource allocation."""
        self.alloc_memory -= float(sandbox.mem_limit.strip("m"))
        self.alloc_cpu -= sandbox.cpu_quota / 100000.0
        sandbox.close()

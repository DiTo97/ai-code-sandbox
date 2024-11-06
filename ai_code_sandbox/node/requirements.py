compliance_script = """
const { exec } = require('child_process');


class SandboxRequirementsError extends Error {
    constructor(requirements) {
        const message = `The following packages are missing or have conflicts: ${requirements.join(', ')}`;
        super(message);
    }
}


function _single_compliance(package) {
    return new Promise((resolve) => {
        const [requirement, specifier] = package.split('@');

        exec(`npm list ${requirement} --depth=0 --json`, (error, stdout) => {
            if (error) {
                resolve(package);
                return;
            }

            try {
                const version = JSON.parse(stdout).dependencies[requirement].version;

                if (specifier && specifier !== version) {
                    resolve(`${package} (version conflict: available ${version})`);
                } else {
                    resolve(null);
                }
            } catch (_) {
                resolve(`${package} (invalid version requirement)`);
            }
        });
    });
}


async function compliance(requirements) {
    const missing = await Promise.all(requirements.map(_single_compliance));
    const missing = missing.filter(result => result !== null);

    if (missing.length > 0) {
        throw new SandboxRequirementsError(missing);
    }
}


(async () => {
    const requirements = {{requirements}};

    try {
        await compliance(requirements);
        process.exit(0);
    } catch (e) {
        console.error(e.message);
        process.exit(1);
    }
})();
"""
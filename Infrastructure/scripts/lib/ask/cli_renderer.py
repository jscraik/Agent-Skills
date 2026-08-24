from ask.cli_human_error import render_error
from ask.cli_human_success import render_success
from ask.cli_output import compact_package_verify_payload, compact_skill_prove_payload


def render_result(parser, repo_root, args, result):
    if (
        args.json
        and args.topic == "skills"
        and args.action == "package"
        and args.target == "verify"
    ):
        compact_package_verify_payload(result.data)
    if args.json and args.topic == "skills" and args.action == "prove":
        compact_skill_prove_payload(result.data)
    if args.json:
        print(result.to_json(repo_root=str(repo_root)))
    elif result.status == "success":
        render_success(parser, args, result)
    else:
        render_error(args, result)

"""Local regression tests. SDK/LLM mocks do not prove GenVM or network consensus."""
import itertools
import json
import pathlib
import types
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
NAME = ROOT.name.removeprefix("genlayer-")


class StorageGeneric:
    @classmethod
    def __class_getitem__(cls, _):
        return cls

    def __init__(self, *args, **kwargs):
        raise TypeError("this class can't be instantiated by user")


class Event:
    def emit(self):
        pass


class Model:
    responses = []
    prompts = []
    override = None

    @classmethod
    def exec_prompt(cls, prompt, **kwargs):
        cls.prompts.append(prompt)
        value = cls.responses.pop(0)
        if isinstance(value, Exception):
            raise value
        return value

    @classmethod
    def comparative(cls, fn, **kwargs):
        # Execute both paths independently; enforce exact stable fields here.
        # Real comparative uses an LLM comparator and must be tested in Studio.
        if cls.override is not None:
            return cls.override
        first = fn()
        second = fn()
        if first != second:
            raise ValueError("mock validator disagreement")
        return first


gl = types.SimpleNamespace(
    Contract=object, Event=Event,
    public=types.SimpleNamespace(write=lambda fn: fn, view=lambda fn: fn),
    message=types.SimpleNamespace(sender_address="creator"),
    vm=types.SimpleNamespace(UserError=ValueError),
    nondet=types.SimpleNamespace(exec_prompt=Model.exec_prompt),
    eq_principle=types.SimpleNamespace(prompt_comparative=Model.comparative),
)
ns = dict(gl=gl, TreeMap=StorageGeneric, DynArray=StorageGeneric,
          Address=str, u256=int, allow_storage=lambda cls: cls)
source = (ROOT / "contract.py").read_text()
assert "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" in source
assert source.splitlines()[0].startswith('# { "Depends":')
assert source.splitlines()[1] == "", "Separate runner JSON from descriptive comments"
exec(compile(source.replace("from genlayer import *", ""), str(ROOT / "contract.py"), "exec"), ns)
Contract = ns[{"roundtrip": "RoundTrip", "counterfactual": "Counterfactual",
               "calibration": "Calibration"}[NAME]]


def fresh(**options):
    gl.message.sender_address = "creator"
    Model.responses, Model.prompts, Model.override = [], [], None
    c = Contract()
    c.cases = {}
    if NAME == "roundtrip":
        c.open_case("case", "Rephrase faithfully", "Restore English", "quantity\ndeadline")
    elif NAME == "counterfactual":
        c.open_case("case", options.get("mode", "all"), options.get("k", 2),
                    "\n".join("condition-" + str(i) for i in range(options.get("n", 3))))
    else:
        c.open_case("case", "tentative: no direct support\nlikely: some support\ncertain: conclusive support",
                    options.get("flag_under", True))
    return c


def submit(c, **options):
    if NAME == "roundtrip":
        return c.submit_source("case", options.get("text", "ORIGINAL_ONLY_719: 3 units due Friday"))
    if NAME == "counterfactual":
        return c.submit_subject("case", options.get("text", "Documented subject facts"))
    return c.submit_assertion("case", options.get("text", "The build passes"),
                              options.get("band", 1), options.get("evidence", "A signed test report"))


def outputs(value):
    if NAME == "roundtrip":
        return [{"text": "forward text"}, {"text": "backward text"}, {"survived": value}]
    return [{("met" if NAME == "counterfactual" else "warranted"): value}]


def run(c, value):
    Model.responses = outputs(value) * 2
    c.evaluate("case")
    return json.loads(c.get_result("case"))


class Regression(unittest.TestCase):
    def test_outcomes(self):
        if NAME == "roundtrip":
            for bits, expected, mask in [([1, 1], 1, 0), ([1, 0], 2, 2), ([0, 0], 2, 3)]:
                c = fresh()
                submit(c)
                r = run(c, bits)
                self.assertEqual((r["outcome"], r["lost_mask"]), (expected, mask))
                self.assertEqual(len(c.lost_aspects("case")), 2 - sum(bits))
                self.assertEqual(len(Model.prompts), 6)
                self.assertNotIn("ORIGINAL_ONLY_719", Model.prompts[1])
                self.assertNotIn("ORIGINAL_ONLY_719", Model.prompts[4])
                self.assertIn("forward text", Model.prompts[1])
        elif NAME == "counterfactual":
            # Exhaust every met vector and threshold up to five conditions.
            for n in range(1, 6):
                for mode in ["all", "kofn"]:
                    for k in range(1, n + 1):
                        for bits in itertools.product([0, 1], repeat=n):
                            c = fresh(n=n, mode=mode, k=k)
                            submit(c)
                            r = run(c, list(bits))
                            need = max(0, (n if mode == "all" else k) - sum(bits))
                            expected = sum(1 << i for i in [i for i, bit in enumerate(bits) if not bit][:need])
                            self.assertEqual(r["change_mask"], expected)
                            self.assertEqual(r["met_mask"], sum(bit << i for i, bit in enumerate(bits)))
                            self.assertEqual(r["outcome"], 1 if need == 0 else 2)
                            self.assertEqual(len(c.minimal_change("case")), need)
        else:
            for flag in [False, True]:
                for claimed in range(3):
                    for warranted in range(3):
                        c = fresh(flag_under=flag)
                        submit(c, band=claimed)
                        r = run(c, warranted)
                        expected = 2 if claimed > warranted else 3 if flag and claimed < warranted else 1
                        self.assertEqual(r["outcome"], expected)
                        self.assertEqual(r["warranted_band"], warranted)
                        self.assertNotIn("claimed_band", Model.prompts[0])

    def test_authorization_and_single_submission(self):
        c = fresh()
        gl.message.sender_address = "stranger"
        with self.assertRaisesRegex(ValueError, "NOT_CREATOR"):
            submit(c)
        gl.message.sender_address = "creator"
        commitment = submit(c)
        self.assertEqual(len(commitment), 64)
        with self.assertRaisesRegex(ValueError, "ALREADY_SUBMITTED"):
            submit(c)

    def test_input_guards(self):
        c = fresh()
        with self.assertRaises(Exception):
            c.evaluate("case")
        for text in ["", " ", "x" * 10001]:
            with self.assertRaises(Exception):
                submit(c, text=text)
        if NAME == "calibration":
            for band in [-1, 3]:
                with self.assertRaises(Exception):
                    submit(c, band=band)
            submit(c, evidence="")  # Missing evidence is permitted, not fabricated.

    def test_creation_guards(self):
        c = Contract()
        c.cases = {}
        def opening(id, rows):
            if NAME == "roundtrip":
                return c.open_case(id, "forward", "inverse", rows)
            if NAME == "counterfactual":
                return c.open_case(id, "all", 0, rows)
            return c.open_case(id, rows, True)
        for id in ["", " ", "x" * 65]:
            with self.assertRaises(Exception):
                opening(id, "a\nb")
        for rows in ["", "a\nA", "x" * 501, "\n".join(str(i) for i in range(13))]:
            with self.assertRaises(Exception):
                opening("invalid", rows)
        opening("valid", "a\nb")
        with self.assertRaises(Exception):
            opening("valid", "a\nb")

    def test_malformed_model_answers(self):
        invalid = [None, True, 1.5, "1", -1, 3] if NAME == "calibration" else [
            None, "11", [True, 1], [1.0, 0], [2, 0], [], [1] * 20]
        for value in invalid:
            c = fresh()
            submit(c)
            r = run(c, value)
            self.assertEqual(r["outcome"], ns["R_UNDETERMINED"])
        for raw in ["not json", "[]", "{}"]:
            c = fresh()
            submit(c)
            Model.responses = [raw]
            c.evaluate("case")
            self.assertEqual(c.get_outcome("case"), ns["R_UNDETERMINED"])

    def test_consensus_payload_validation(self):
        for payload in [{}, {"h": "wrong"}, {"h": "wrong", "warranted": True}]:
            c = fresh()
            submit(c)
            Model.override = json.dumps(payload)
            c.evaluate("case")
            self.assertEqual(c.get_outcome("case"), ns["R_UNDETERMINED"])
        # Also reject bad decision fields even when the commitment is correct.
        c = fresh()
        h = submit(c)
        Model.override = json.dumps({"h": h, "survived": [True, 1],
                                     "met": [1, 0, 2], "warranted": 1.5})
        c.evaluate("case")
        self.assertEqual(c.get_outcome("case"), ns["R_UNDETERMINED"])

    def test_input_commitments(self):
        fields = {"roundtrip": [("source", "changed"), ("inverse", "changed")],
                  "counterfactual": [("subject", "changed"), ("k", 1)],
                  "calibration": [("evidence", "changed"), ("flag_under", False),
                                  ("claimed_band", 2)]}[NAME]
        for field, value in fields:
            c = fresh()
            submit(c)
            setattr(c.cases["case"], field, value)
            c.evaluate("case")
            self.assertEqual(c.get_outcome("case"), ns["R_UNDETERMINED"])
            self.assertEqual(Model.prompts, [])

    def test_terminal_and_permissionless_evaluation(self):
        for fail in [False, True]:
            c = fresh()
            submit(c)
            gl.message.sender_address = "any-evaluator"
            value = 1 if NAME == "calibration" else [1, 1] if NAME == "roundtrip" else [1, 1, 1]
            Model.responses = [ValueError("model unavailable")] if fail else outputs(value) * 2
            c.evaluate("case")
            before = c.get_result("case")
            with self.assertRaises(Exception):
                c.evaluate("case")
            self.assertEqual(c.get_result("case"), before)
            gl.message.sender_address = "creator"
            with self.assertRaises(Exception):
                submit(c)

    def test_independent_paths_and_disagreement(self):
        c = fresh()
        submit(c)
        a = 0 if NAME == "calibration" else [1, 1] if NAME == "roundtrip" else [1, 1, 1]
        b = 2 if NAME == "calibration" else [0, 0] if NAME == "roundtrip" else [0, 0, 0]
        Model.responses = outputs(a) + outputs(b)
        c.evaluate("case")
        self.assertEqual(c.get_outcome("case"), ns["R_UNDETERMINED"])
        self.assertGreaterEqual(len(Model.prompts), 2)

    def test_result_visibility(self):
        c = fresh()
        pending = json.loads(c.get_result("case"))
        self.assertEqual(pending["outcome"], 0)
        if NAME == "calibration":
            self.assertIsNone(pending["warranted_band"])
        submit(c)
        Model.responses = [ValueError("failure")]
        c.evaluate("case")
        result = json.loads(c.get_result("case"))
        self.assertEqual(len(result["result_hash"]), 64)
        self.assertEqual(result["reason"], "judge-failed")
        if NAME == "calibration":
            self.assertIsNone(result["warranted_band"])
            self.assertEqual(result["warranted_label"], "")


if __name__ == "__main__":
    unittest.main(verbosity=2)

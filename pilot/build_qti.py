"""
Render the pilot JSON bank into a Canvas-importable QTI 1.2 package.
This is the artifact that gets hand-tested against a Canvas sandbox --
per the pipeline spec, nothing here is trusted until that import succeeds.
"""
import json
import hashlib
import zipfile
import os
from xml.sax.saxutils import escape

with open("1.1-pilot.json") as f:
    ITEMS = json.load(f)

QUIZ_TITLE = "Section 1.1 Pilot Bank (Sets: Basic Concepts)"
QUIZ_IDENT = "g" + hashlib.md5(QUIZ_TITLE.encode()).hexdigest()[:31]


def ident_for(item_id, salt=""):
    return "g" + hashlib.md5((item_id + salt).encode()).hexdigest()[:31]


def esc(text):
    return escape(str(text))


def material_block(text, indent="          "):
    return f'{indent}<material>\n{indent}  <mattext texttype="text/plain">{esc(text)}</mattext>\n{indent}</material>'


def build_mc_item(item, points=1.0):
    """multiple_choice and true_false share this shape."""
    item_ident = ident_for(item["id"])
    resp_ident = ident_for(item["id"], "response1")
    options = item["options"]
    answer = item["answer"]

    # normalize true/false answer (python bool) to matching option text
    if item["item_format"] == "true_false":
        answer_text = "True" if answer is True else "False"
    else:
        answer_text = answer

    label_idents = [ident_for(item["id"], f"opt{i}") for i in range(len(options))]
    correct_label = None
    labels_xml = []
    for i, (opt_text, opt_ident) in enumerate(zip(options, label_idents)):
        if opt_text == answer_text:
            correct_label = opt_ident
        labels_xml.append(f"""        <response_label ident="{opt_ident}">
{material_block(opt_text, indent="          ")}
        </response_label>""")
    if correct_label is None:
        raise ValueError(f"Could not match answer to an option for {item['id']}")

    question_type_field = "true_false_question" if item["item_format"] == "true_false" else "multiple_choice_question"

    feedback_xml = ""
    fb = item.get("feedback") or {}
    if fb.get("correct"):
        feedback_xml += f"""  <itemfeedback ident="correct_fb">
    <flow_mat>
      <material>
        <mattext texttype="text/plain">{esc(fb['correct'])}</mattext>
      </material>
    </flow_mat>
  </itemfeedback>
"""
    if fb.get("incorrect"):
        feedback_xml += f"""  <itemfeedback ident="general_incorrect_fb">
    <flow_mat>
      <material>
        <mattext texttype="text/plain">{esc(fb['incorrect'])}</mattext>
      </material>
    </flow_mat>
  </itemfeedback>
"""

    return f"""<item ident="{item_ident}" title="{esc(item['id'])}">
  <itemmetadata>
    <qtimetadata>
      <qtimetadatafield><fieldlabel>question_type</fieldlabel><fieldentry>{question_type_field}</fieldentry></qtimetadatafield>
      <qtimetadatafield><fieldlabel>points_possible</fieldlabel><fieldentry>{points}</fieldentry></qtimetadatafield>
    </qtimetadata>
  </itemmetadata>
  <presentation>
{material_block(item['stem'], indent="    ")}
    <response_lid ident="{resp_ident}" rcardinality="Single">
      <render_choice>
{chr(10).join(labels_xml)}
      </render_choice>
    </response_lid>
  </presentation>
  <resprocessing>
    <outcomes>
      <decvar maxvalue="100" minvalue="0" varname="SCORE" vartype="Decimal"/>
    </outcomes>
    <respcondition continue="No">
      <conditionvar>
        <varequal respident="{resp_ident}">{correct_label}</varequal>
      </conditionvar>
      <setvar action="Set" varname="SCORE">100</setvar>
    </respcondition>
  </resprocessing>
{feedback_xml}</item>"""


def build_numeric_item(item, points=1.0):
    item_ident = ident_for(item["id"])
    resp_ident = ident_for(item["id"], "response1")
    answer = item["answer"]
    fb = item.get("feedback") or {}
    feedback_xml = ""
    if fb.get("correct"):
        feedback_xml += f"""  <itemfeedback ident="correct_fb">
    <flow_mat><material><mattext texttype="text/plain">{esc(fb['correct'])}</mattext></material></flow_mat>
  </itemfeedback>
"""
    if fb.get("incorrect"):
        feedback_xml += f"""  <itemfeedback ident="general_incorrect_fb">
    <flow_mat><material><mattext texttype="text/plain">{esc(fb['incorrect'])}</mattext></material></flow_mat>
  </itemfeedback>
"""
    return f"""<item ident="{item_ident}" title="{esc(item['id'])}">
  <itemmetadata>
    <qtimetadata>
      <qtimetadatafield><fieldlabel>question_type</fieldlabel><fieldentry>numerical_question</fieldentry></qtimetadatafield>
      <qtimetadatafield><fieldlabel>points_possible</fieldlabel><fieldentry>{points}</fieldentry></qtimetadatafield>
    </qtimetadata>
  </itemmetadata>
  <presentation>
{material_block(item['stem'], indent="    ")}
    <response_num ident="{resp_ident}" rcardinality="Single">
      <render_fib fibtype="Decimal">
        <response_label ident="answer1"/>
      </render_fib>
    </response_num>
  </presentation>
  <resprocessing>
    <outcomes>
      <decvar maxvalue="100" minvalue="0" varname="SCORE" vartype="Decimal"/>
    </outcomes>
    <respcondition continue="No">
      <conditionvar>
        <and>
          <vargte respident="{resp_ident}">{answer}</vargte>
          <varlte respident="{resp_ident}">{answer}</varlte>
        </and>
      </conditionvar>
      <setvar action="Set" varname="SCORE">100</setvar>
    </respcondition>
  </resprocessing>
{feedback_xml}</item>"""


# Accepted-answer overrides for short_answer items where the JSON `answer`
# field mixes the gradable value with explanatory text.
SHORT_ANSWER_OVERRIDES = {
    "contemath-1.1-pilot-C-02": ["∅", "{}", "{ }", "empty set", "null set"],
    "contemath-1.1-pilot-C-03": ["{i}"],
}


def build_short_answer_item(item, points=1.0):
    item_ident = ident_for(item["id"])
    resp_ident = ident_for(item["id"], "response1")
    accepted = SHORT_ANSWER_OVERRIDES.get(item["id"], [str(item["answer"])])
    fb = item.get("feedback") or {}
    feedback_xml = ""
    if fb.get("correct"):
        feedback_xml += f"""  <itemfeedback ident="correct_fb">
    <flow_mat><material><mattext texttype="text/plain">{esc(fb['correct'])}</mattext></material></flow_mat>
  </itemfeedback>
"""
    if fb.get("incorrect"):
        feedback_xml += f"""  <itemfeedback ident="general_incorrect_fb">
    <flow_mat><material><mattext texttype="text/plain">{esc(fb['incorrect'])}</mattext></material></flow_mat>
  </itemfeedback>
"""
    conditions = "\n".join(
        f'          <varequal respident="{resp_ident}" case="No">{esc(a)}</varequal>' for a in accepted
    )
    return f"""<item ident="{item_ident}" title="{esc(item['id'])}">
  <itemmetadata>
    <qtimetadata>
      <qtimetadatafield><fieldlabel>question_type</fieldlabel><fieldentry>short_answer_question</fieldentry></qtimetadatafield>
      <qtimetadatafield><fieldlabel>points_possible</fieldlabel><fieldentry>{points}</fieldentry></qtimetadatafield>
    </qtimetadata>
  </itemmetadata>
  <presentation>
{material_block(item['stem'], indent="    ")}
    <response_str ident="{resp_ident}" rcardinality="Single">
      <render_fib>
        <response_label ident="answer1"/>
      </render_fib>
    </response_str>
  </presentation>
  <resprocessing>
    <outcomes>
      <decvar maxvalue="100" minvalue="0" varname="SCORE" vartype="Decimal"/>
    </outcomes>
    <respcondition continue="No">
      <conditionvar>
        <or>
{conditions}
        </or>
      </conditionvar>
      <setvar action="Set" varname="SCORE">100</setvar>
    </respcondition>
  </resprocessing>
{feedback_xml}<!-- NOTE: {len(accepted)} accepted-answer variant(s) configured: {', '.join(accepted)} -->
</item>"""


def build_essay_item(item, points=1.0):
    item_ident = ident_for(item["id"])
    resp_ident = ident_for(item["id"], "response1")
    return f"""<item ident="{item_ident}" title="{esc(item['id'])}">
  <itemmetadata>
    <qtimetadata>
      <qtimetadatafield><fieldlabel>question_type</fieldlabel><fieldentry>essay_question</fieldentry></qtimetadatafield>
      <qtimetadatafield><fieldlabel>points_possible</fieldlabel><fieldentry>{points}</fieldentry></qtimetadatafield>
    </qtimetadata>
  </itemmetadata>
  <presentation>
{material_block(item['stem'], indent="    ")}
    <response_str ident="{resp_ident}" rcardinality="Single">
      <render_fib>
        <response_label ident="answer1"/>
      </render_fib>
    </response_str>
  </presentation>
  <resprocessing>
    <outcomes>
      <decvar maxvalue="100" minvalue="0" varname="SCORE" vartype="Decimal"/>
    </outcomes>
  </resprocessing>
  <!-- Manually graded: model answer / rubric lives in the JSON record's `answer` and `notes` fields -->
</item>"""


BUILDERS = {
    "multiple_choice": build_mc_item,
    "true_false": build_mc_item,
    "numeric_entry": build_numeric_item,
    "short_answer": build_short_answer_item,
    "essay": build_essay_item,
}

item_xml_blocks = []
skipped = []
for item in ITEMS:
    builder = BUILDERS.get(item["item_format"])
    if not builder:
        skipped.append(item["id"])
        continue
    item_xml_blocks.append(builder(item))

assessment_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<questestinterop xmlns="http://www.imsglobal.org/xsd/ims_qtiasiv1p2"
                  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                  xsi:schemaLocation="http://www.imsglobal.org/xsd/ims_qtiasiv1p2 http://www.imsglobal.org/xsd/ims_qtiasiv1p2p1.xsd">
  <assessment ident="{QUIZ_IDENT}" title="{esc(QUIZ_TITLE)}">
    <qtimetadata>
      <qtimetadatafield><fieldlabel>cc_maxattempts</fieldlabel><fieldentry>1</fieldentry></qtimetadatafield>
    </qtimetadata>
    <section ident="root_section">
{chr(10).join(item_xml_blocks)}
    </section>
  </assessment>
</questestinterop>
"""

points_possible = sum(1 for i in ITEMS if i["item_format"] != "essay") + sum(1 for i in ITEMS if i["item_format"] == "essay")

assessment_meta_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<quiz identifier="{QUIZ_IDENT}" xmlns="http://canvas.instructure.com/xsd/cccv1p0">
  <title>{esc(QUIZ_TITLE)}</title>
  <description>&lt;p&gt;Pilot bank for the problem-bank pipeline: algorithmic (Category A, auto-verified), templated (Category B, needs_review), and static (Category C, needs_review) items covering multiple_choice, true_false, numeric_entry, short_answer, and essay formats. Source: OpenStax Contemporary Mathematics 1.1, CC BY 4.0.&lt;/p&gt;</description>
  <shuffle_answers>false</shuffle_answers>
  <scoring_policy>keep_highest</scoring_policy>
  <hide_results></hide_results>
  <quiz_type>practice_quiz</quiz_type>
  <points_possible>{points_possible}</points_possible>
  <require_lockdown_browser>false</require_lockdown_browser>
  <require_lockdown_browser_for_results>false</require_lockdown_browser_for_results>
  <allowed_attempts>1</allowed_attempts>
  <one_question_at_a_time>false</one_question_at_a_time>
  <cant_go_back>false</cant_go_back>
  <available>true</available>
</quiz>
"""

manifest_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<manifest identifier="man_{QUIZ_IDENT}"
          xmlns="http://www.imsglobal.org/xsd/imscp_v1p1"
          xmlns:lom="http://ltsc.ieee.org/xsd/LOM"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://www.imsglobal.org/xsd/imscp_v1p1 http://www.imsglobal.org/profile/cc/ccv1p1/ccv1p1_imscp_v1p2_v1p0.xsd">
  <metadata>
    <schema>IMS Content</schema>
    <schemaversion>1.1.3</schemaversion>
  </metadata>
  <organizations/>
  <resources>
    <resource identifier="{QUIZ_IDENT}" type="imsqti_xmlv1p2" intendeduse="assessment">
      <file href="{QUIZ_IDENT}/{QUIZ_IDENT}.xml"/>
      <dependency identifierref="{QUIZ_IDENT}_meta"/>
    </resource>
    <resource identifier="{QUIZ_IDENT}_meta" type="associatedcontent/imscc_xmlv1p1/learning-application-resource" href="{QUIZ_IDENT}/assessment_meta.xml">
      <file href="{QUIZ_IDENT}/assessment_meta.xml"/>
    </resource>
  </resources>
</manifest>
"""

os.makedirs(QUIZ_IDENT, exist_ok=True)
with open(f"{QUIZ_IDENT}/{QUIZ_IDENT}.xml", "w", encoding="utf-8") as f:
    f.write(assessment_xml)
with open(f"{QUIZ_IDENT}/assessment_meta.xml", "w", encoding="utf-8") as f:
    f.write(assessment_meta_xml)
with open("imsmanifest.xml", "w", encoding="utf-8") as f:
    f.write(manifest_xml)

zip_name = "contemath-1.1-pilot-qti.zip"
with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as z:
    z.write("imsmanifest.xml")
    z.write(f"{QUIZ_IDENT}/{QUIZ_IDENT}.xml")
    z.write(f"{QUIZ_IDENT}/assessment_meta.xml")

print(f"Built {len(item_xml_blocks)} QTI items ({len(skipped)} skipped: {skipped})")
print(f"Wrote {zip_name}")

# -*- coding: utf-8 -*-
#
# Copyright (c) 2020, Geoffrey M. Poore
# All rights reserved.
#
# Licensed under the BSD 3-Clause License:
# http://opensource.org/licenses/BSD-3-Clause
#


from .quiz import Quiz, Question, GroupStart, GroupEnd, TextRegion


# QTI 2.1 uses a different structure than QTI 1.2
# QTI 2.1 uses assessmentTest and assessmentItem elements
BEFORE_ITEMS = '''\
<?xml version="1.0" encoding="UTF-8"?>
<assessmentTest xmlns="http://www.imsglobal.org/xsd/imsqti_v2p1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.imsglobal.org/xsd/imsqti_v2p1 http://www.imsglobal.org/xsd/imsqti_v2p1.xsd" identifier="{assessment_identifier}" title="{title}">
  <testPart identifier="testpart1" navigationMode="nonlinear" submissionMode="individual">
    <assessmentSection identifier="root_section" title="{title}">
'''

AFTER_ITEMS = '''\
    </assessmentSection>
  </testPart>
  <outcomeDeclaration identifier="SCORE" baseType="float" cardinality="single"/>
  <outcomeDeclaration identifier="MAXSCORE" baseType="float" cardinality="single">
    <defaultValue>
      <value>{points_possible}</value>
    </defaultValue>
  </outcomeDeclaration>
</assessmentTest>
'''

GROUP_START = '''\
      <assessmentSection identifier="{ident}" title="{group_title}">
        <selection>
          <selectionNumber>{pick}</selectionNumber>
        </selection>
        <rubricBlock identifier="points_per_item" view="author">
          <p>Points per item: {points_per_item}</p>
        </rubricBlock>
'''

GROUP_END = '''\
      </assessmentSection>
'''

TEXT = '''\
      <assessmentItemRef identifier="{ident}" href="{href}"/>
'''

START_ITEM = '''\
      <assessmentItem identifier="{question_identifier}" title="{question_title}" adaptive="false" timeDependent="false">
'''

END_ITEM = '''\
      </assessmentItem>
'''

ITEM_METADATA = '''\
        <responseDeclaration identifier="RESPONSE" baseType="{base_type}" cardinality="{cardinality}">
{response_declaration_body}
        </responseDeclaration>
        <outcomeDeclaration identifier="SCORE" baseType="float" cardinality="single">
          <defaultValue>
            <value>0</value>
          </defaultValue>
        </outcomeDeclaration>
        <outcomeDeclaration identifier="MAXSCORE" baseType="float" cardinality="single">
          <defaultValue>
            <value>{points_possible}</value>
          </defaultValue>
        </outcomeDeclaration>
'''

ITEM_BODY_MCTF = '''\
        <itemBody>
          <p>{question_html_xml}</p>
          <choiceInteraction responseIdentifier="RESPONSE" shuffle="{shuffle}" maxChoices="1">
{choices}
          </choiceInteraction>
        </itemBody>
'''

ITEM_BODY_MULTANS = '''\
        <itemBody>
          <p>{question_html_xml}</p>
          <choiceInteraction responseIdentifier="RESPONSE" shuffle="{shuffle}" maxChoices="{max_choices}">
{choices}
          </choiceInteraction>
        </itemBody>
'''

ITEM_BODY_CHOICE = '''\
            <simpleChoice identifier="{ident}" fixed="false">{choice_html_xml}</simpleChoice>
'''

ITEM_BODY_SHORTANS = '''\
        <itemBody>
          <p>{question_html_xml}</p>
          <textEntryInteraction responseIdentifier="RESPONSE" expectedLength="50"/>
        </itemBody>
'''

ITEM_BODY_ESSAY = '''\
        <itemBody>
          <p>{question_html_xml}</p>
          <extendedTextInteraction responseIdentifier="RESPONSE" expectedLength="1000"/>
        </itemBody>
'''

ITEM_BODY_UPLOAD = '''\
        <itemBody>
          <p>{question_html_xml}</p>
          <uploadInteraction responseIdentifier="RESPONSE"/>
        </itemBody>
'''

ITEM_BODY_NUM = '''\
        <itemBody>
          <p>{question_html_xml}</p>
          <textEntryInteraction responseIdentifier="RESPONSE" baseType="float" expectedLength="20"/>
        </itemBody>
'''

RESPONSE_PROCESSING_MCTF = '''\
        <responseProcessing>
          <responseCondition>
            <responseIf>
              <match>
                <variable identifier="RESPONSE"/>
                <correct identifier="RESPONSE"/>
              </match>
              <setOutcomeValue identifier="SCORE">
                <sum>
                  <variable identifier="SCORE"/>
                  <baseValue baseType="float">{points_possible}</baseValue>
                </sum>
              </setOutcomeValue>
{correct_feedback}
            </responseIf>
{incorrect_feedback}
{general_feedback}
          </responseCondition>
        </responseProcessing>
'''

RESPONSE_PROCESSING_MULTANS = '''\
        <responseProcessing>
          <responseCondition>
            <responseIf>
              <and>
{match_conditions}
              </and>
              <setOutcomeValue identifier="SCORE">
                <sum>
                  <variable identifier="SCORE"/>
                  <baseValue baseType="float">{points_possible}</baseValue>
                </sum>
              </setOutcomeValue>
{correct_feedback}
            </responseIf>
{incorrect_feedback}
{general_feedback}
          </responseCondition>
        </responseProcessing>
'''

RESPONSE_PROCESSING_SHORTANS = '''\
        <responseProcessing>
          <responseCondition>
            <responseIf>
              <or>
{varequal_conditions}
              </or>
              <setOutcomeValue identifier="SCORE">
                <sum>
                  <variable identifier="SCORE"/>
                  <baseValue baseType="float">{points_possible}</baseValue>
                </sum>
              </setOutcomeValue>
{correct_feedback}
            </responseIf>
{incorrect_feedback}
{general_feedback}
          </responseCondition>
        </responseProcessing>
'''

RESPONSE_PROCESSING_NUM = '''\
        <responseProcessing>
          <responseCondition>
            <responseIf>
              <and>
                <gte>
                  <variable identifier="RESPONSE"/>
                  <baseValue baseType="float">{num_min}</baseValue>
                </gte>
                <lte>
                  <variable identifier="RESPONSE"/>
                  <baseValue baseType="float">{num_max}</baseValue>
                </lte>
              </and>
              <setOutcomeValue identifier="SCORE">
                <sum>
                  <variable identifier="SCORE"/>
                  <baseValue baseType="float">{points_possible}</baseValue>
                </sum>
              </setOutcomeValue>
{correct_feedback}
            </responseIf>
{incorrect_feedback}
{general_feedback}
          </responseCondition>
        </responseProcessing>
'''

RESPONSE_PROCESSING_ESSAY = '''\
        <responseProcessing>
          <responseCondition>
            <responseIf>
              <isNull>
                <variable identifier="RESPONSE"/>
              </isNull>
              <setOutcomeValue identifier="SCORE">
                <baseValue baseType="float">0</baseValue>
              </setOutcomeValue>
            </responseIf>
{general_feedback}
          </responseCondition>
        </responseProcessing>
'''

RESPONSE_PROCESSING_UPLOAD = RESPONSE_PROCESSING_ESSAY

MATCH_CONDITION = '''\
                <match>
                  <variable identifier="RESPONSE"/>
                  <baseValue baseType="identifier">{ident}</baseValue>
                </match>
'''

VARQUAL_CONDITION = '''\
                <match>
                  <variable identifier="RESPONSE"/>
                  <baseValue baseType="string">{answer_xml}</baseValue>
                </match>
'''

FEEDBACK_CORRECT = '''\
              <setOutcomeValue identifier="FEEDBACK">
                <baseValue baseType="string">{feedback}</baseValue>
              </setOutcomeValue>
'''

FEEDBACK_INCORRECT = '''\
            <responseElse>
              <setOutcomeValue identifier="FEEDBACK">
                <baseValue baseType="string">{feedback}</baseValue>
              </setOutcomeValue>
            </responseElse>
'''

FEEDBACK_GENERAL = '''\
            <responseElse>
              <setOutcomeValue identifier="FEEDBACK">
                <baseValue baseType="string">{feedback}</baseValue>
              </setOutcomeValue>
            </responseElse>
'''

FEEDBACK_CHOICE = '''\
              <setOutcomeValue identifier="FEEDBACK">
                <baseValue baseType="string">{feedback}</baseValue>
              </setOutcomeValue>
'''


def assessment_v2(*, quiz: Quiz, assessment_identifier: str, title_xml: str) -> str:
    '''
    Generate QTI 2.1 assessment XML from Quiz.
    '''
    xml = []
    xml.append(BEFORE_ITEMS.format(assessment_identifier=assessment_identifier,
                                   title=title_xml))
    
    # Calculate total points for MAXSCORE
    points_possible = 0
    for x in quiz.questions_and_delims:
        if isinstance(x, Question):
            points_possible += x.points_possible
        elif isinstance(x, GroupStart):
            points_possible += x.group.points_per_question * x.group.pick
    
    for question_or_delim in quiz.questions_and_delims:
        if isinstance(question_or_delim, TextRegion):
            # QTI 2.1 doesn't have a direct text-only question type
            # We'll create a simple item with just text
            item_id = f'qtimaker_text_{question_or_delim.id}'
            xml.append(f'      <assessmentItem identifier="{item_id}" title="{question_or_delim.title_xml}" adaptive="false" timeDependent="false">')
            xml.append('        <itemBody>')
            xml.append(f'          <p>{question_or_delim.text_html_xml}</p>')
            xml.append('        </itemBody>')
            xml.append('        <outcomeDeclaration identifier="SCORE" baseType="float" cardinality="single">')
            xml.append('          <defaultValue>')
            xml.append('            <value>0</value>')
            xml.append('          </defaultValue>')
            xml.append('        </outcomeDeclaration>')
            xml.append('        <responseProcessing>')
            xml.append('          <responseCondition/>')
            xml.append('        </responseProcessing>')
            xml.append('      </assessmentItem>')
            continue
        if isinstance(question_or_delim, GroupStart):
            xml.append(GROUP_START.format(ident=f'qtimaker_group_{question_or_delim.group.id}',
                                          group_title=question_or_delim.group.title_xml,
                                          pick=question_or_delim.group.pick,
                                          points_per_item=question_or_delim.group.points_per_question))
            continue
        if isinstance(question_or_delim, GroupEnd):
            xml.append(GROUP_END)
            continue
        if not isinstance(question_or_delim, Question):
            raise TypeError
        question = question_or_delim

        xml.append(START_ITEM.format(question_identifier=f'qtimaker_question_{question.id}',
                                     question_title=question.title_xml))

        # Response declaration based on question type
        if question.type in ('true_false_question', 'multiple_choice_question', 'multiple_answers_question'):
            base_type = 'identifier'
            cardinality = 'multiple' if question.type == 'multiple_answers_question' else 'single'
            correct_responses = []
            for choice in question.choices:
                if choice.correct:
                    correct_responses.append(f'            <correctResponse><value>{choice.id}</value></correctResponse>')
            response_declaration_body = '\n'.join(correct_responses) if correct_responses else ''
        elif question.type == 'short_answer_question':
            base_type = 'string'
            cardinality = 'single'
            correct_responses = []
            for choice in question.choices:
                correct_responses.append(f'            <correctResponse><value>{choice.choice_xml}</value></correctResponse>')
            response_declaration_body = '\n'.join(correct_responses)
        elif question.type == 'numerical_question':
            base_type = 'float'
            cardinality = 'single'
            if question.numerical_exact is not None:
                response_declaration_body = f'            <correctResponse><value>{question.numerical_exact_html_xml}</value></correctResponse>'
            else:
                response_declaration_body = f'            <correctResponse><value>{question.numerical_min_html_xml}</value></correctResponse>'
        else:
            # Essay and upload don't have response declarations
            response_declaration_body = ''
            base_type = 'string'
            cardinality = 'single'

        if question.type not in ('essay_question', 'file_upload_question'):
            xml.append(ITEM_METADATA.format(base_type=base_type,
                                           cardinality=cardinality,
                                           response_declaration_body=response_declaration_body,
                                           points_possible=question.points_possible))

        # Item body
        shuffle = 'true' if quiz.shuffle_answers_xml == 'true' else 'false'
        if question.type in ('true_false_question', 'multiple_choice_question'):
            choices = '\n'.join(ITEM_BODY_CHOICE.format(ident=f'qtimaker_choice_{c.id}',
                                                       choice_html_xml=c.choice_html_xml)
                               for c in question.choices)
            xml.append(ITEM_BODY_MCTF.format(question_html_xml=question.question_html_xml,
                                             shuffle=shuffle,
                                             choices=choices))
        elif question.type == 'multiple_answers_question':
            choices = '\n'.join(ITEM_BODY_CHOICE.format(ident=f'qtimaker_choice_{c.id}',
                                                       choice_html_xml=c.choice_html_xml)
                               for c in question.choices)
            xml.append(ITEM_BODY_MULTANS.format(question_html_xml=question.question_html_xml,
                                               shuffle=shuffle,
                                               max_choices=len(question.choices),
                                               choices=choices))
        elif question.type == 'short_answer_question':
            xml.append(ITEM_BODY_SHORTANS.format(question_html_xml=question.question_html_xml))
        elif question.type == 'numerical_question':
            xml.append(ITEM_BODY_NUM.format(question_html_xml=question.question_html_xml))
        elif question.type == 'essay_question':
            xml.append(ITEM_BODY_ESSAY.format(question_html_xml=question.question_html_xml))
        elif question.type == 'file_upload_question':
            xml.append(ITEM_BODY_UPLOAD.format(question_html_xml=question.question_html_xml))
        else:
            raise ValueError

        # Response processing
        correct_feedback = ''
        incorrect_feedback = ''
        general_feedback = ''
        
        if question.correct_feedback_raw is not None:
            correct_feedback = FEEDBACK_CORRECT.format(feedback=question.correct_feedback_html_xml)
        if question.incorrect_feedback_raw is not None:
            incorrect_feedback = FEEDBACK_INCORRECT.format(feedback=question.incorrect_feedback_html_xml)
        if question.feedback_raw is not None:
            general_feedback = FEEDBACK_GENERAL.format(feedback=question.feedback_html_xml)

        if question.type in ('true_false_question', 'multiple_choice_question'):
            xml.append(RESPONSE_PROCESSING_MCTF.format(points_possible=question.points_possible,
                                                       correct_feedback=correct_feedback,
                                                       incorrect_feedback=incorrect_feedback,
                                                       general_feedback=general_feedback))
        elif question.type == 'multiple_answers_question':
            match_conditions = []
            for choice in question.choices:
                if choice.correct:
                    match_conditions.append(MATCH_CONDITION.format(ident=f'qtimaker_choice_{choice.id}'))
            xml.append(RESPONSE_PROCESSING_MULTANS.format(match_conditions='\n'.join(match_conditions),
                                                         points_possible=question.points_possible,
                                                         correct_feedback=correct_feedback,
                                                         incorrect_feedback=incorrect_feedback,
                                                         general_feedback=general_feedback))
        elif question.type == 'short_answer_question':
            varequal_conditions = []
            for choice in question.choices:
                varequal_conditions.append(VARQUAL_CONDITION.format(answer_xml=choice.choice_xml))
            xml.append(RESPONSE_PROCESSING_SHORTANS.format(varequal_conditions='\n'.join(varequal_conditions),
                                                          points_possible=question.points_possible,
                                                          correct_feedback=correct_feedback,
                                                          incorrect_feedback=incorrect_feedback,
                                                          general_feedback=general_feedback))
        elif question.type == 'numerical_question':
            xml.append(RESPONSE_PROCESSING_NUM.format(num_min=question.numerical_min_html_xml,
                                                     num_max=question.numerical_max_html_xml,
                                                     points_possible=question.points_possible,
                                                     correct_feedback=correct_feedback,
                                                     incorrect_feedback=incorrect_feedback,
                                                     general_feedback=general_feedback))
        elif question.type == 'essay_question':
            xml.append(RESPONSE_PROCESSING_ESSAY.format(general_feedback=general_feedback))
        elif question.type == 'file_upload_question':
            xml.append(RESPONSE_PROCESSING_UPLOAD.format(general_feedback=general_feedback))
        else:
            raise ValueError

        xml.append(END_ITEM)

    xml.append(AFTER_ITEMS.format(points_possible=points_possible))

    return ''.join(xml)


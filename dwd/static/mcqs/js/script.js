
var McqObj = {
  questions: [],
  /* `len` would be the total number of questions */
  len: 0,
  /* `curQuesIndex` is the index of current question */
  curQuesIndex: -1,
  switchNextQues: '',
  switchPrevQues: ''
};

$(document).ready(function() {
    /* CSRF Token */
    var csrfmiddlewaretoken = $.cookie("csrftoken");

    McqObj.questions = MCQs;
    McqObj.len = MCQs.length;
    McqObj.curQuesIndex = -1;

    switchQuestion(0);

    var panel = $("#question_no_panel");
    /* Create panel buttons */
    var panelButtons = "";
    for (i = 0; i < McqObj.len; i++) {
      if (Answers[String(i+1)] === "" || typeof Answers[String(i+1)] === "undefined") {
        panelButton = '<span class="qno-panel-label" id="qno' + String(i+1) + '">' + String(i+1) + '</span>';
      } else {
        panelButton = '<span class="qno-panel-label answered" id="qno' + String(i+1) + '">' + String(i+1) + '</span>';
      }
      panelButtons += panelButton;
    }
    /* Add buttons to panel */
    panel.html(panelButtons);

  $(document).on("click", ".qno-panel-label", function() {
    var $this = $(this);
    var qno = parseInt($this.text());
    var index = qno - 1;
    switchQuestion(index);
  });

  $("#next_question").click(function() {
    McqObj.switchNextQues();
  });

  $("#prev_question").click(function() {
    McqObj.switchPrevQues();
  });

  McqObj.switchNextQues = function() {
    var i = McqObj.curQuesIndex;
    i = (i == McqObj.len-1) ? 0 : ++i;
    switchQuestion(i);
  };

  McqObj.switchPrevQues = function() {
    var i = McqObj.curQuesIndex;
    i = (i === 0) ? McqObj.len-1 : --i;
    switchQuestion(i);
  };

  function switchQuestion(index) {
    if (index == McqObj.curQuesIndex) {
      return;
    }

    var choices = "";
    var question = McqObj.questions[index];

    $("#question_and_choices_panel").fadeOut(300, function() {
      $("#question_no").text("Q" + String(question.qno));
      /* Convert Markdown text to HTML */
      var qtextHtml = showdownConverter.makeHtml(question.qtext);

      $("#question_text").html(qtextHtml);

      /* Highlightjs */
      $("pre code").each(function(i, block) {
        hljs.highlightBlock(block);
      });

      $.each(question.choices, function(i, choice) {
        /* Highlight the choice if it has already been selected as answer */
        var choiceid = "choiceno" + String(choice.no);
        if (choice.no == Answers[String(question.qno)] && typeof Answers[String(question.qno)] != "undefined") {
          div = '<div class="ui segment inverted teal choice" onclick="selectChoice(this)" id="' + choiceid + '">' + choice.text + '</div>';
        } else {
          div = '<div class="ui segment choice" onclick="selectChoice(this)" id="' + choiceid + '">' + choice.text + '</div>';
        }

        choices +=  div;
      });
      $("#choices").html(choices);
    }).fadeIn(300);

    McqObj.curQuesIndex = index;

  }

  window.selectChoice = function selectChoice(ele) {
    var selectedChoiceId = $(ele).attr("id");
    var choiceno = parseInt(selectedChoiceId.slice("choiceno".length));
    var curQuesNo = String(McqObj.curQuesIndex+1);
    Answers[curQuesNo] = choiceno;
    $(ele).addClass("teal inverted");

    /* Mark Question as answered in question_no_panel */
    $("#qno" + curQuesNo).addClass("answered");

    /* Switch to next question */
    McqObj.switchNextQues();
  };

  $("#submit_all").click(function() {

    /* If all questions have not been solved */
    if (Object.keys(Answers).length != McqObj.len) {
      var submitAnswers = confirm("You have not answered all questions. Would you still like to continue uploading answers?");
      /* If user cancels confirmation, don't upload answers */
      if (submitAnswers === false) {
        return;
      }
    }

    var data = Answers;
    data.csrfmiddlewaretoken = csrfmiddlewaretoken;
    $.post("/mcqs/answer/", data, function() {
      console.log("Answers uploaded.");
      alert("Answers uploaded.");
    }).fail(function() {
      console.log("Error occured while uploading answers.");
      alert("Error occured while uploading answers.");
    });
  });

});

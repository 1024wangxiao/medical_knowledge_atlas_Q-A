;
var member_qa_ops={
    init:function(){
        this.eventBind();
    },

    eventBind:function(){
        $(".question_wrap .do-question").click(function(){
                var btn_target=$(this);
                if (btn_target.hasClass("disabled")){
                    common_ops.alert("正在处理!!!请不要重复点击")
                    return;
                }
                var question=$(".question_wrap textarea[name=question]").val();
                var username=$(".question_wrap input[name=username]").val();
                if (username==undefined||username.length<1){
                    common_ops.alert("请输入您的姓名，然后再使用问答功能");
                    return;
                }
                if (question==undefined || question.length<1){
                    common_ops.alert("请输入您想要询问的问题，然后再按确定");
                    return;
                }
                btn_target.addClass('disabled');
                $.ajax({
                    url:common_ops.buildUrl("/member/analysis"),
                    type:"POST",
                    data:{
                            Username:username,
                            Text:question,
                    },
                    dataType:'json',
                    success:function(res){
                        btn_target.removeClass('disabled');
                        var callback =null;
                        if (res.code == 200){
                             callback=function(data){
                                 var reply=res.data
                                 window.location.href=common_ops.buildUrl("/member/QA");
                         };
                        }
                        common_ops.alert(res.data,callback);
                    }
                });

        });
    }

};
$(document).ready(function(){
    member_qa_ops.init();


});
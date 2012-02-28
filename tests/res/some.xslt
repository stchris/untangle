<?xml version="1.0" ?>
<xsl:stylesheet version="1.0">
    <xsl:template match="math">
        <table class="compact">
            <tr>
                <xsl:for-each select="m_expr">
                    <td class="compact vam">
                        <xsl:apply-templates />
                    </td>
                </xsl:for-each>
            </tr>
        </table>
    </xsl:template>

    <xsl:template match="m_expr"/>

    <xsl:template match="m_lit">
        <p class="compact tac formula">
            <xsl:apply-templates />
        </p>
    </xsl:template>

    <xsl:template match="m_var">
        <p class="compact tac formula italic">
            <xsl:apply-templates />
        </p>
    </xsl:template>
</xsl:stylesheet>
